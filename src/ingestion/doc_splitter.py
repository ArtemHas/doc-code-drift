from langchain_text_splitters import MarkdownHeaderTextSplitter


class MarkdownDocSplitter:
    def __init__(self):
        self.headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ]
        
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )

    def split_file(self, file_path: str) -> list[dict]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except FileNotFoundError:
            print(f"Файл не найден: {file_path}")
            return []

        splits = self.splitter.split_text(markdown_text)

        result = []
        for i, split in enumerate(splits):
            result.append({
                "chunk_id": i + 1,
                "content": split.page_content,
                "context": split.metadata 
            })

        return result


def main():
    splitter = MarkdownDocSplitter()
    readme_path = "data/raw/spring-petclinic/readme.md"
    
    chunks = splitter.split_file(readme_path)
    
    print(f"--- Успешно разрезано на логических секций: {len(chunks)} ---\n")
    
    for chunk in chunks[:2]:
        print(f"📄 СЕКЦИЯ #{chunk['chunk_id']}")
        print(f"📍 Контекст (Заголовки): {chunk['context']}")
        print(f"📝 Текст куска:\n{chunk['content'][:150]}...")
        print("-" * 50)


if __name__ == "__main__":
    main()