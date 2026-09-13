import re
from sentence_transformers import SentenceTransformer, util

class EntityResolver:

    def __init__(
        self, 
        model_name : str = "all-MiniLM-L6-v2",
        threshold: float = 0.78
        ):
        """
            model_name: lightweight, fast embedding model (~80 MB).
            threshold: confidence threshold (from 0 to 1). We consider everything above to be one
            and the same.
        """
        print(f"Downloading the embedding model")

        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

    def _normalize_name(self,name:str)->str:
        """breaking camelCase ('findOwner' -> 'find Owner'),

        so that the neural network can better understand individual English words.
        """

        words = re.sub("([a-z])([A-Z])", r"\1 \2", name)
        return words.lower().strip()

    def resolve_entities(
        self, code_entities : list[str],
        doc_entities : list[str]
        ) -> list[dict]:
        """Compares the list of entities from the code with the list from the documentation.
        Returns the found synonym pairs.
        """
        
        matches = []

        # 1. preparing normalized strings for the embedding model

        normalized_code = [self._normalize_name(c) for c in code_entities]
        normalized_doc = [self._normalize_name(d) for d in doc_entities]

        # 2 100 % match cases
        unmatched_doc_indices = set(range(len(doc_entities)))

        for i, code_item in enumerate(normalized_code):
            for j in list(unmatched_doc_indices):
                doc_item = normalized_doc[j]

                if code_item == doc_item:
                    matches.append(
                        {
                            "code_entity" : code_entities[i], 
                            "doc_entity": doc_entities[j], 
                            "similarity" : 1.0, 
                            "match_type" : "EXACT",
                        }
                    )
                    unmatched_doc_indices.remove(j)
        # for those that are not 100 % equal
        remaining_doc_indices = list(unmatched_doc_indices)
        if not remaining_doc_indices:
            return matches
        
        remaining_doc_texts = [
            normalized_doc[j] for j in remaining_doc_indices
        ]

        # turning text & code into embeddings

        code_embeddings = self.model.encode(
            normalized_code, convert_to_tensor = True
        )
        doc_embeddings = self.model.encode(
            remaining_doc_texts, convert_to_tensor = True
        )

        # counting the matrix of cosine similarity
        
        cosine_scores = util.cos_sim(code_embeddings, doc_embeddings)

 

        # searching matches that exceeded the threshold

        for i, code_item in enumerate(code_entities):
            for k, doc_idx in enumerate(remaining_doc_indices):
                score = float(cosine_scores[i][k])

                if score >= self.threshold:
                    matches.append(
                        {
                            "code_entity" : code_item, 
                            "doc_entity" : doc_entities[doc_idx],
                            "similarity" : round(score ,4), 
                            "match_type" : "SEMANTIC_VECTOR", 
                        }
                    ) 
        return matches
# --- ТЕСТОВЫЙ БЛОК ---
def main():
    resolver = EntityResolver(threshold=0.80)

    # 1. Реальные методы из Java-кода PetClinic:
    code_methods = ["findOwner", "savePet", "initCreationForm", "getVisits"]

    # 2. Синонимы и фразы, которые извлекла LLM из текста README.md:
    doc_terms = [
        "findOwner",  # Точное совпадение
        "searchOwner",  # Синоним к findOwner
        "storePet",  # Синоним к savePet
        "createForm",  # Похоже на initCreationForm
        "deleteDatabase",  # Мусор (этого нет в коде, не должно сматчиться)
    ]

    print("\n--- Запуск Entity Resolution (Склейка синонимов) ---")
    results = resolver.resolve_entities(code_methods, doc_terms)

    for match in results:
        print(
            f"🔗 Код: `{match['code_entity']}`  <===>  Доки: `{match['doc_entity']}`"
        )
        print(
            f"   Сходство: {match['similarity']} | Тип: {match['match_type']}\n"
        )


if __name__ == "__main__":
    main()