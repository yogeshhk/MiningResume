# 🚀 Quick Start Guide - LLM Resume Parser v2.0

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd C:\TFS\Study\MiningResume\src

# Install dependencies using uv (recommended)
uv pip install --system
```

### Step 2: Configure Environment

```bash
# Copy the environment template
copy .env.example .env

# Edit .env file (optional - works without for local models)
# If using HuggingFace API, add your token:
# HUGGINGFACEHUB_API_TOKEN=your_token_here
```

### Step 3: Test the Installation

```bash
# Run the example script
python example_usage.py
```

## Usage Examples

### Option 1: Command-Line Interface (Recommended for beginners)

```bash
# Parse a single file
python -m llm-based.cli parse --file data/YogeshKulkarniLinkedInProfile.pdf

# Parse multiple files in a folder
python -m llm-based.cli parse --folder data/

# With additional options
python -m llm-based.cli parse --file resume.pdf --verbose --no-cache

# Get help
python -m llm-based.cli --help
```

### Option 2: Python API (For integration)

```python
from pathlib import Path
from src.llm_based.core.models import ParserConfig
# See example_usage.py for complete code
```

## Expected Output

```json
{
  "filename": "resume.pdf",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1 (555) 123-4567",
  "skills": "Python, JavaScript, SQL",
  "employment_history": "Senior Engineer at Tech Corp...",
  "education_history": "BS Computer Science...",
  ...
}
```

## Troubleshooting

### "Module not found" errors
- Run: `uv pip install --system`

### Model download takes long
- First run downloads the model (~2GB for flan-t5-large)
- Subsequent runs use cached model

### Out of memory errors
- Use smaller model: `--model google/flan-t5-base`
- Or reduce max_tokens in config

## What's Different from v1.0?

| Feature | v1.0 (old) | v2.0 (new) |
|---------|------------|------------|
| Architecture | Monolithic | Modular (SOLID) |
| Error Handling | Basic try-catch | Retry + fallback |
| Logging | Print statements | Structured JSON logs |
| Caching | None | Automatic with TTL |
| Testing | None | Unit tests included |
| LLM Providers | HuggingFace only | Pluggable interface |
| Configuration | Hardcoded | Environment-based |
| CLI | None | Full CLI support |

## Next Steps

1. ✅ Parse your first resume
2. ✅ Check the logs folder for detailed logs
3. ✅ Customize prompts in `src.llm_based/config/prompts.yaml`
4. ✅ Read full documentation in `src.llm_based/README.md`
5. ✅ Run tests: `pytest`

## Need Help?

- Full docs: `src/src.llm_based/README.md`
- Implementation details: `src/IMPLEMENTATION_SUMMARY.md`
- Example code: `src/example_usage.py`
- Test examples: `src/tests/`

---

**Ready to parse!** 🎉
