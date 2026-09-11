import tree_sitter_java as tsjava
from tree_sitter import Language, Parser


class JavaASTParser:
    def __init__(self):
        # initializing language and parser
        self.JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(self.JAVA_LANGUAGE)

    def parse_file(self, file_path: str) -> list[dict[str, str]]:
        try:
            with open(file_path, "rb") as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Файл не найден: {file_path}")
            return []

        tree = self.parser.parse(source_code)

        entities = []

        self._traverse_node(tree.root_node, entities, current_class=None)
        return entities

    def _traverse_node(self, node, entities: list[dict], current_class: str | None):
        # 1. If a node is a class declaration
        if node.type == "class_declaration":
            # searching the node with the 'identifier type'
            for child in node.children:
                if child.type == "identifier":
                    class_name = child.text.decode("utf-8")
                    entities.append(
                        {"type": "class", "name": class_name, "parent": None}
                    )
                    current_class = class_name
                    break

        # 2. if node is a method declaration
        elif node.type == "method_declaration":
            for child in node.children:
                if child.type == "identifier":
                    method_name = child.text.decode("utf-8")
                    entities.append(
                        {"type": "method", "name": method_name, "parent": current_class}
                    )
                    break

        # 3. recursively going to the children nodes
        for child in node.children:
            self._traverse_node(child, entities, current_class)



