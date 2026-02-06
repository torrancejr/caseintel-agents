"""
Integration tests for the document analysis pipeline.
"""
import pytest
import asyncio
from src.workflows.discovery_pipeline import run_pipeline
from src.workflows.state import DocumentType, PrivilegeFlag


@pytest.fixture
def sample_contract_text():
    """Sample contract text for testing."""
    return """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement is entered into as of January 15, 2024,
    between Acme Corporation ("Employer") and John Smith ("Employee").
    
    1. POSITION: Employee shall serve as Senior Software Engineer.
    2. COMPENSATION: Annual salary of $150,000.
    3. TERM: Two (2) years commencing February 1, 2024.
    4. NON-COMPETE: 24 months, 50-mile radius.
    5. GOVERNING LAW: State of New York.
    
    Executed on January 15, 2024.
    """


@pytest.fixture
def sample_email_text():
    """Sample email text for testing."""
    return """
    From: attorney@lawfirm.com
    To: client@company.com
    Date: March 10, 2024
    Subject: PRIVILEGED AND CONFIDENTIAL - Legal Strategy
    
    Dear Client,
    
    This email contains attorney-client privileged information regarding
    our litigation strategy. Please do not share with anyone outside
    the legal team.
    
    Based on my analysis, I recommend we pursue settlement negotiations
    rather than proceeding to trial.
    
    Best regards,
    Attorney Name
    """


@pytest.mark.asyncio
async def test_contract_classification(sample_contract_text):
    """Test that a contract is correctly classified."""
    result = await run_pipeline(
        document_url="test://contract.pdf",
        case_id="test_case_001",
        job_id="test_job_001",
        raw_text=sample_contract_text
    )
    
    assert result["status"] == "completed"
    assert result["document_type"] == DocumentType.CONTRACT
    assert result["classification_confidence"] > 0.7
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_metadata_extraction(sample_contract_text):
    """Test metadata extraction from contract."""
    result = await run_pipeline(
        document_url="test://contract.pdf",
        case_id="test_case_002",
        job_id="test_job_002",
        raw_text=sample_contract_text
    )
    
    # Check dates extracted
    assert result["dates"] is not None
    assert len(result["dates"]) > 0
    
    # Check people extracted
    assert result["people"] is not None
    assert any("John Smith" in p.get("name", "") for p in result["people"])
    
    # Check entities extracted
    assert result["entities"] is not None
    assert any("Acme" in e.get("name", "") for e in result["entities"])


@pytest.mark.asyncio
async def test_privilege_detection(sample_email_text):
    """Test privilege detection in attorney-client email."""
    result = await run_pipeline(
        document_url="test://email.eml",
        case_id="test_case_003",
        job_id="test_job_003",
        raw_text=sample_email_text
    )
    
    # Should detect privilege
    assert result["privilege_flags"] is not None
    assert PrivilegeFlag.ATTORNEY_CLIENT in result["privilege_flags"] or \
           PrivilegeFlag.CONFIDENTIAL in result["privilege_flags"]
    assert result["privilege_confidence"] > 0.5


@pytest.mark.asyncio
async def test_content_analysis(sample_contract_text):
    """Test content analysis generates summary and key facts."""
    result = await run_pipeline(
        document_url="test://contract.pdf",
        case_id="test_case_004",
        job_id="test_job_004",
        raw_text=sample_contract_text
    )
    
    # Check summary generated
    assert result["summary"] is not None
    assert len(result["summary"]) > 50
    
    # Check key facts extracted
    assert result["key_facts"] is not None
    assert len(result["key_facts"]) > 0
    
    # Check legal issues identified
    assert result["legal_issues"] is not None


@pytest.mark.asyncio
async def test_pipeline_progress():
    """Test that pipeline progress updates correctly."""
    result = await run_pipeline(
        document_url="test://document.pdf",
        case_id="test_case_005",
        job_id="test_job_005",
        raw_text="Sample document text for testing."
    )
    
    # Pipeline should complete
    assert result["status"] == "completed"
    assert result["progress_percent"] == 100
    assert result["current_agent"] is None


@pytest.mark.asyncio
async def test_error_handling():
    """Test pipeline handles errors gracefully."""
    # Empty text should not crash pipeline
    result = await run_pipeline(
        document_url="test://empty.pdf",
        case_id="test_case_006",
        job_id="test_job_006",
        raw_text=""
    )
    
    # Should complete even with empty text
    assert result["status"] in ["completed", "failed"]
    assert result["progress_percent"] >= 0


def test_document_type_enum():
    """Test DocumentType enum values."""
    assert DocumentType.CONTRACT == "contract"
    assert DocumentType.EMAIL == "email"
    assert DocumentType.DEPOSITION == "deposition"


def test_privilege_flag_enum():
    """Test PrivilegeFlag enum values."""
    assert PrivilegeFlag.ATTORNEY_CLIENT == "attorney_client"
    assert PrivilegeFlag.WORK_PRODUCT == "work_product"
    assert PrivilegeFlag.CONFIDENTIAL == "confidential"
    assert PrivilegeFlag.NONE == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
