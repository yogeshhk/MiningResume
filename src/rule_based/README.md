# rule_based

Regex-driven resume parser. No LLM or network call required.

## How it works

1. `regex_config.xml` declares the fields to extract, the extraction method, and the patterns/keywords to use.
2. `RegexResumeParser` reads a resume file (PDF, DOCX, or TXT) and runs each configured rule against the text.

Three extraction methods are supported:

| Method | What it does |
|--------|-------------|
| `section_extractor` | Segments the resume into named sections (e.g. Skills, Education) based on heading keywords |
| `univalue_extractor` | Extracts a single value (e.g. Name, Email) using a regex pattern |
| `section_value_extractor` | Scans a specific section for keyword matches and assembles a list of values |

## Usage

```python
from src.rule_based.regex_resume_parser import RegexResumeParser

with open("src/rule_based/regex_config.xml", "r") as f:
    config_content = f.read()

parser = RegexResumeParser(config_content=config_content)
parser.read_resume_file("data/resume.pdf")
result = parser.parse()   # returns an OrderedDict
```

Or run via the top-level entry point with `MODE = "rule"` in `src/main.py`.

## Customising extraction rules

Edit `regex_config.xml` — no Python changes needed. Each `<term>` element defines:
- `name` — output key (e.g. `Name`, `Skills`)
- child element `method name` — one of the three methods above
- child element `section` — which section to search (leave blank to search the full text)
- pattern/keyword child elements — the regex patterns or keyword lists to match
