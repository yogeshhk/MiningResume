# Migration Guide: v1.0 → v2.0

## Overview

This guide helps you migrate from the original `llm_resume_parser.py` to the new modular v2.0 architecture.

## Key Changes

### 1. Package Structure

**Before (v1.0):**
```
llm_resume_parser.py  # Single file, ~164 lines
```

**After (v2.0):**
```
llm_parser/           # Full package with ~3000+ lines
├── core/             # Models, interfaces, exceptions
├── services/         # Business logic
├── adapters/         # External integrations
├── utils/            # Utilities
└── config/           # Configuration
```

### 2. Import Changes

**Before:**
```python
from llm_resume_parser import LLMResumeParser

parser = LLMResumeParser()
```

**After:**
```python
# Option 1: Use the setup helper
from example_usage import setup_parser

parser = setup_parser()

# Option 2: Manual setup (full control)
from llm_parser.core.models import ParserConfig
from llm_parser.services.parser_service import ParserService
# ... (see example_usage.py)
```

### 3. Configuration Changes

**Before:**
```python
# Hardcoded in class
parser = LLMResumeParser(
    model_name="google/flan-t5-large",
    temperature=1e-10
)
```

**After:**
```python
# Via environment variables (.env file)
# Or programmatically:
config = ParserConfig(
    model_name="google/flan-t5-large",
    temperature=1e-10,
    cache_enabled=True,
)
```

### 4. Usage Changes

**Before:**
```python
# Parse single file
resume = parser.read_single_resume("resume.pdf")
parsed = parser.parse_resume(resume['resume_text'])
print(json.dumps(parsed, indent=4))
```

**After:**
```python
# Parse single file
result = parser.parse_single(Path("resume.pdf"))
if result.success:
    print(result.extracted_data.to_json(indent=2))
```

### 5. Error Handling

**Before:**
```python
try:
    parsed = parser.parse_resume(text)
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
# Errors are captured in result
result = parser.parse_single(file_path)
if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Details: {result.error_details}")
```

## Dependency Management Update

- Dependencies are now installed using `uv`:
  ```bash
  uv pip install --system
  ```
- This replaces manual `pip install` and ensures your environment matches the project specification.

## Side-by-Side Comparison

### Old Code (v1.0)

```python
import os
import json
from llm_resume_parser import LLMResumeParser

# Setup
parser = LLMResumeParser()

# Parse
resume = parser.read_single_resume("data/resume.pdf")
if resume:
    parsed_data = parser.parse_resume(resume['resume_text'])
    parsed_data['filename'] = resume['filename']
    
    json_result = json.dumps(parsed_data, indent=4)
    print(json_result)
```

### New Code (v2.0)

```python
from pathlib import Path
from example_usage import setup_parser

# Setup (with caching, retry, logging, etc.)
parser = setup_parser()

# Parse (automatic error handling)
result = parser.parse_single(Path("data/resume.pdf"))

# Output
if result.success:
    print(result.extracted_data.to_json(indent=2))
    print(f"Processing time: {result.processing_time_seconds:.2f}s")
else:
    print(f"Error: {result.error_message}")
```

## Migration Strategies

### Strategy 1: Gradual Migration (Recommended)

1. Keep `llm_resume_parser.py` unchanged
2. Install new dependencies: `pip install -r requirements_new.txt`
3. Test new code alongside old code
4. Migrate scripts one at a time

### Strategy 2: Fresh Start

1. Install dependencies
2. Use `example_usage.py` as template
3. Copy your resume files to `data/`
4. Run and verify outputs

### Strategy 3: CLI Only

1. Install dependencies
2. Use CLI instead of Python API:
   ```bash
   python -m llm_parser.cli parse --file resume.pdf
   ```

## Feature Mapping

| v1.0 Feature | v2.0 Equivalent | Notes |
|--------------|-----------------|-------|
| `read_single_resume()` | `parser.parse_single()` | Now includes parsing |
| `read_resumes_from_folder()` | `parser.parse_batch()` | Batch processing |
| `parse_resume()` | Built into `parse_single()` | Automatic |
| Exception handling | `ParserResult.success` | Structured results |
| Print logging | `StructuredLogger` | JSON logs |
| No retry | Automatic retry | With backoff |
| No caching | Automatic caching | With TTL |

## Backward Compatibility

### Can I still use v1.0?

**Yes!** The old `llm_resume_parser.py` file is **unchanged** and will continue to work.

### Do I need to update?

**No, but recommended.** v2.0 offers:
- Better error handling
- Performance improvements (caching)
- Better observability (logging)
- Easier testing
- More maintainable code

### Can I use both?

**Yes!** They are independent:

```python
# Old code
from llm_resume_parser import LLMResumeParser
old_parser = LLMResumeParser()

# New code
from llm_parser.services.parser_service import ParserService
# new_parser = ...
```

## Common Issues & Solutions

### Issue: "Module not found: llm_parser"

**Solution:** The new code is in a package. Use:
```python
from llm_parser import ...
# Or run from src/ directory
```

### Issue: "Pydantic not found"

**Solution:** Install new dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "My old script broke"

**Solution:** Old code should still work. If not:
1. Check you're using old imports: `from llm_resume_parser import ...`
2. The new code doesn't affect old code

### Issue: "Output format changed"

**Solution:** v2.0 uses Pydantic models:
```python
# Get dict like v1.0
data_dict = result.extracted_data.to_dict()

# Get JSON string
json_str = result.extracted_data.to_json(indent=2)
```

## Testing Your Migration

### Step 1: Verify Old Code Still Works

```bash
python llm_resume_parser.py
# Should work as before
```

### Step 2: Test New Code

```bash
python example_usage.py
# Should parse successfully
```

### Step 3: Compare Outputs

Parse the same resume with both versions and compare results.

## Getting Help

- Full documentation: `llm_parser/README.md`
- Quick start: `QUICKSTART.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Example code: `example_usage.py`

## Rollback Plan

If you need to roll back:

1. The old code is **untouched** - just use it
2. Uninstall new packages if needed:
   ```bash
   pip uninstall pydantic pydantic-settings
   ```
3. Your old scripts will work as before

---

**Remember:** You can take your time migrating. Both versions coexist peacefully! 🤝
