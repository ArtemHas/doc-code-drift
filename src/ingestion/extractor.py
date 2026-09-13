from enum import Enum

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

#1 list of allowed relations between objects 
class RelationType(str, Enum):
    CALLS = "CALLS" # a method calls another method
    CONFIGURES = "CONFIGURES" #set up (e.g. database, port etc.)
    USER_CLASS = "USER_CLASS" #documentation section uses this specific class
    THROWS = "THROWS" # An error or an exception
#2 the triplet scheme
class KnowledgeTriplet(BaseModel):
    subject : str = Field(
        description = "the source entity (for example, the name of a class or component from the text)"
    )
    relation : RelationType = Field(
        description = "the relation type from the permitted list"
    )
    object : str = Field(
        description = "Entity-goal (what it’s associated with: method, database, parameter)"
    )
#3 list of found triplets
class ExtractedKnowledge(BaseModel):
    triplets : list[KnowledgeTriplet] = Field(
        default_factory = list, description = "List of found relations"
    )
#4 extractor class
class DocEntityExtractor:
    def __init__(
        self,
        base_url : str = "http://localhost:11434/v1", 
        model: str = "qwen2.5:7b",
    ):
        #By default, we connect to the local Ollama (for free and locally).
        self.client = instructor.from_openai(
            OpenAI(base_url = base_url, api_key="ollama"),
            mode = instructor.Mode.JSON,
        )
        self.model = model; 
    
    def extract_triplets(self, text_chunk : str) -> list[KnowledgeTriplet]:
        #Sends the text to the LLM and forces the data to be returned strictly according to our Pydantic schema.

        prompt = f"""
            You are a system code analyst. Analyze this fragment of technical documentation. Extract only the key software facts: which classes, components, or databases are mentioned and how they are connected.
        
            RAGMENT OF DOCUMENTATION:
            {text_chunk}
        """

        try:
            response : ExtractedKnowledge = self.client.chat.completions.create(
                model = self.model, 
                response_model = ExtractedKnowledge, 
                messages = [{"role": "user", "content" : prompt}],
                temperature = 0.0,
            )
            return response.triplets
        except Exception as e:
            print(f"Error with LLM : {e}")
            return []
    
    def filter_hallucinations(
        self, 
        triplets: list[KnowledgeTriplet], 
        code_whitelist: set[str],
    ) -> list[KnowledgeTriplet]:
        """HALLUCINATION FILTER:

        Checks that either the subject or the object actually exists in the code
        (is on the whitelist). If the AI has made up both names, we reject it.
        """
        valid_triplets = []
        for t in triplets:
            if t.subject in code_whitelist or t.object in code_whitelist:
                valid_triplets.append(t)
            else:
                print(
                    f"⚠️ THE HALLUCINATION HAS BEEN DISCARDED: ({t.subject}) -> [{t.relation}] -> ({t.object})"
                )
        return valid_triplets
# --- ТЕСТОВЫЙ БЛОК ---
def main():
    # 1. Представим "Белый список", который наш AST-парсер реально нашел в Java-коде PetClinic:
    mock_code_whitelist = {"Owner", "Pet", "Vet", "PetClinicApplication"}

    # 2. Кусок текста из документации (где упоминается реальный класс и пара посторонних вещей):
    sample_text = """
    The PetClinicApplication is the main entry point of the project.
    It configures the embedded database and manages entities like Owner and Pet.
    Also, users love playing with funny dogs outside.
    """

    print("--- Запуск экстракции через LLM ---")
    extractor = DocEntityExtractor()

    # Извлекаем факты
    raw_triplets = extractor.extract_triplets(sample_text)
    print(f"ИИ нашел сырых фактов: {len(raw_triplets)}")
    for t in raw_triplets:
        print(f"  🤖 ({t.subject}) --[{t.relation}]--> ({t.object})")

    # Прогоняем через фильтр белого списка
    print("\n--- Фильтрация по белому списку кода ---")
    clean_triplets = extractor.filter_hallucinations(
        raw_triplets, mock_code_whitelist
    )
    print(f"Осталось проверенных фактов: {len(clean_triplets)}")
    for t in clean_triplets:
        print(f"  ✅ ({t.subject}) --[{t.relation}]--> ({t.object})")


if __name__ == "__main__":
    main()