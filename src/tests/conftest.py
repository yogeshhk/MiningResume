"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from llm_parser.core.models import (
    ResumeDocument,
    ExtractedResume,
    ParserConfig,
    LLMRequest,
    LLMResponse,
    FileFormat,
)


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Email: john.doe@example.com
    Phone: +1 (555) 123-4567
    
    Summary:
    Experienced software engineer with 5+ years in Python development.
    
    Skills:
    Python, JavaScript, SQL, Docker, AWS
    
    Experience:
    Senior Software Engineer, Tech Corp, 2020-Present
    - Led development of microservices architecture
    - Mentored junior developers
    
    Education:
    BS Computer Science, University of Tech, 2015-2019
    """


@pytest.fixture
def sample_resume_document(tmp_path):
    """Create a sample resume document."""
    file_path = tmp_path / "test_resume.txt"
    file_path.write_text("Sample resume content")

    return ResumeDocument(
        file_path=file_path,
        filename="test_resume.txt",
        file_format=FileFormat.TXT,
        file_size_bytes=len("Sample resume content"),
    )


@pytest.fixture
def sample_extracted_resume():
    """Sample extracted resume data."""
    return ExtractedResume(
        filename="test_resume.pdf",
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+1 (555) 123-4567",
        skills="Python, JavaScript, SQL",
        employment_history="Senior Software Engineer at Tech Corp",
        education_history="BS Computer Science",
    )


@pytest.fixture
def parser_config():
    """Default parser configuration for testing."""
    return ParserConfig(
        model_name="test-model",
        temperature=0.1,
        max_tokens=100,
        cache_enabled=False,
        max_retries=1,
    )


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider."""
    provider = Mock()
    provider.get_provider_name.return_value = "mock"
    provider.health_check.return_value = True
    provider.generate.return_value = LLMResponse(
        content="Test response",
        attribute="test",
        model_name="mock-model",
    )
    return provider


@pytest.fixture
def sample_llm_request():
    """Sample LLM request."""
    return LLMRequest(
        prompt="Extract {attribute} from:\n{resume}",
        context="Sample resume text",
        attribute="Name",
    )


@pytest.fixture
def sample_llm_response():
    """Sample LLM response."""
    return LLMResponse(
        content="John Doe",
        attribute="Name",
        tokens_used=50,
        model_name="test-model",
    )

