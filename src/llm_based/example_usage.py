"""
Example script demonstrating usage of the LLM Resume Parser.

This shows how to use the parser programmatically.
"""
from pathlib import Path

from src.llm_based.services.parser_factory import create_parser


def main():
    """Main example execution."""

    print("=== LLM Resume Parser Example ===\n")

    # Get sample resume path
    data_folder = Path(__file__).parent.parent.parent / "data"
    sample_resume = data_folder / "YogeshKulkarniLinkedInProfile.pdf"

    if not sample_resume.exists():
        print(f"Error: Sample resume not found at {sample_resume}")
        print("Please place a resume file in the data folder.")
        return

    print(f"Setting up parser...")
    parser = create_parser()

    print(f"Parsing: {sample_resume.name}\n")

    # Parse the resume
    result = parser.parse_single(sample_resume)

    # Display results
    if result.success:
        print("✅ Parsing successful!\n")
        print("--- Extracted Data ---")
        print(result.extracted_data.to_json(indent=2))

        print(f"\n--- Metrics ---")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"LLM calls: {result.llm_calls_count}")
        print(f"Cache hits: {result.cache_hits_count}")
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.error_message}")


if __name__ == "__main__":
    main()

