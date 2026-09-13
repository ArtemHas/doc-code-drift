# Doc-Code Drift

Система аудита расхождений между исходным кодом и документацией с использованием GraphRAG (Neo4j + LLM).

## 🗂 Структура проекта

```text
.
├── data/                    # Данные для анализа и бенчмарки
│   ├── raw/                 # Склонированные репозитории
│   └── benchmarks/          # Тестовые сценарии расхождений
├── src/                     # Исходный код системы
│   ├── ingestion/           # Сбор и парсинг (AST, Markdown)
│   ├── graph/               # Работа с Neo4j (построение графа)
│   └── audit/               # Поиск дрифта (анализ расхождений)
├── ui/                      # Интерфейс пользователя (Streamlit)
├── tests/                   # Автоматические тесты
├── .env.example             # Конфигурация окружения
└── requirements.txt         # Зависимости проекта
```

## 🚀 Описание модулей
- **ingestion**: Парсит код через Tree-sitter и документацию через LangChain, извлекая сущности.
- **graph**: Формирует базу знаний в Neo4j, связывая элементы кода с их описанием.
- **audit**: Использует LLM-агентов для выявления несоответствий в графе.


### 🚀 Инструкция по запуску:

1. Склонировать репозиторий:
   git clone <...>
   cd doc-code-drift

2. Создать и активировать виртуальное окружение:
   # На Mac/Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # На Windows (сmd):
   python -m venv .venv
   .venv\Scripts\activate.bat

3. Установить все зависимости одной командой:
   pip install -r requirements.txt

4. Скачать тестовый проект
   git clone https://github.com/spring-projects/spring-petclinic.git data/raw/spring-petclinic

