# Minimal entry point with a simple mode switch (Option C)
# Set MODE to "rule" for rule-based regex parser, or "llm" for LLM-based pipeline.
# Adjust FILE_PATH to point to a resume under the repository's data folder.

import json
from pathlib import Path

from llm_based.services.parser_factory import create_parser

# ---- Configuration (edit these constants as needed) ----
MODE = "llm"  # "rule" or "llm"
FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "YogeshKulkarniLinkedInProfile.pdf"
# -------------------------------------------------------


def run_rule_based(file_path: Path) -> None:
    """Run the rule-based parser using regex configuration."""
    from src.rule_based.regex_resume_parser import RegexResumeParser

    # Load regex configuration XML from the rule_based folder
    config_file = Path(__file__).resolve().parent / "rule_based" / "regex_config.xml"
    if not config_file.exists():
        raise FileNotFoundError(f"Regex config not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()

    parser = RegexResumeParser(config_content=config_content)
    resume_data = parser.read_resume_file(str(file_path))
    if not resume_data or not resume_data.get("resume_text", "").strip():
        raise RuntimeError(f"Failed to read resume text from: {file_path}")

    result = parser.parse() or {}
    result["filename"] = file_path.name

    print(json.dumps(result, indent=2))


def run_llm_based(file_path: Path) -> None:
    """Run the LLM-based pipeline with minimal wiring."""
    print("=== LLM Resume Parser Example ===\n")

    if not file_path.exists():
        print(f"Error: Resume not found at {file_path}")
        print("Please place a resume file in the data folder.")
        return

    print(f"Setting up parser...")
    parser = create_parser()

    print(f"Parsing: {file_path.name}\n")

    # Parse the resume
    result = parser.parse_single(file_path)

    # Display results
    if result.success:
        print("✅ Parsing successful!\n")
        print("--- Extracted Data ---")
        print(result.extracted_data.model_dump_json())

        print(f"\n--- Metrics ---")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"LLM calls: {result.llm_calls_count}")
        print(f"Cache hits: {result.cache_hits_count}")
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.error_message}")


def main():
    # Minimal switch with clear comments; no external dependencies beyond src.* modules
    file_path = FILE_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    if MODE == "rule":
        run_rule_based(file_path)
    elif MODE == "llm":
        run_llm_based(file_path)
    else:
        raise ValueError(f"Invalid MODE '{MODE}'. Use 'rule' or 'llm'.")


if __name__ == "__main__":
    main()
