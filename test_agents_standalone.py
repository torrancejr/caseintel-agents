#!/usr/bin/env python3
"""
Standalone test of CaseIntel AI Agents
Tests the agent pipeline directly without database or API
"""
import asyncio
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, '/Users/ryan/WIXEN/CaseIntel/agents')

from src.workflows.discovery_pipeline import run_pipeline

# Test documents
TEST_DOCUMENTS = {
    "contract": """SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 15, 2026, by and between:

Acme Corporation ("Provider")
123 Business St, New York, NY 10001

and

Global Industries Inc. ("Client")
456 Commerce Ave, Los Angeles, CA 90001

WHEREAS, Provider agrees to provide consulting services as outlined in Schedule A;

WHEREAS, Client agrees to pay the fees as specified in Section 3.

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

1. SERVICES
Provider shall provide business consulting services to Client as detailed in the attached Schedule A.

2. TERM
This Agreement shall commence on February 1, 2026 and continue for twelve (12) months.

3. COMPENSATION
Client shall pay Provider $10,000 per month, due on the first day of each month.

4. CONFIDENTIALITY
Both parties agree to maintain confidentiality of proprietary information.

5. TERMINATION
Either party may terminate this Agreement with 30 days written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

Signed: John Smith, CEO, Acme Corporation
Signed: Jane Doe, President, Global Industries Inc.""",

    "privileged": """CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION

From: sarah.johnson@lawfirm.com
To: john.smith@acmecorp.com
Date: January 20, 2026
Subject: Re: Product Liability Strategy - PRIVILEGED

Dear John,

Thank you for meeting with me yesterday regarding the brake pad defect litigation.

As your legal counsel, I must advise you of the following:

1. ATTORNEY WORK PRODUCT
Our analysis shows that the internal emails from March 2025 discussing the known brake defects are highly problematic. The email where your VP of Engineering stated "we should recall but it will cost too much" is particularly damaging.

2. PRIVILEGE PROTECTION
We need to immediately assert attorney-client privilege over all communications regarding this matter. Please do NOT discuss this with anyone outside of legal counsel.

3. LITIGATION STRATEGY
I recommend we:
- File a motion to seal the March 2025 emails
- Prepare for settlement negotiations
- Conduct privilege review of all engineering documents

This communication contains attorney work product and is protected by attorney-client privilege. Do not forward or disclose.

Best regards,
Sarah Johnson, Esq.
Partner, Smith & Johnson LLP
Attorney for Acme Corporation""",

    "smoking_gun": """From: mike.peterson@acmecorp.com
To: lisa.chen@acmecorp.com
Date: March 15, 2025
Subject: Brake Pad Testing Results - URGENT

Lisa,

I just reviewed the Q1 testing data and we have a MAJOR problem.

The new brake pads are failing stress tests at 60% of expected lifespan. This means they could fail catastrophically in real-world conditions, especially in emergency braking situations.

I know we're scheduled to ship 50,000 units next month, but we CANNOT release these. People could die.

I brought this up in yesterday's meeting and was told "the recall cost would exceed our quarterly profit target." When I pressed the issue, Tom said "just make sure this email doesn't leak."

I'm documenting this for the record. We KNOW these brakes are defective. We KNOW they pose a safety risk. And we're choosing profit over safety.

If someone gets hurt, this is on management. I tried to stop it.

I'm copying this to my personal email as backup.

Mike Peterson
Senior QA Engineer
Acme Corporation"""
}


def format_result(doc_type, state):
    """Format pipeline results for display"""
    print(f"\n{'='*70}")
    print(f"🔍 ANALYSIS RESULTS: {doc_type.upper()}")
    print(f"{'='*70}\n")
    
    # Document Classification
    print(f"📋 Document Type: {state.get('document_type', 'N/A')}")
    print(f"   Confidence: {state.get('classification_confidence', 0):.2%}")
    print(f"   Reasoning: {state.get('classification_reasoning', 'N/A')[:200]}...")
    print()
    
    # Metadata
    dates = state.get('dates', [])
    people = state.get('people', [])
    entities = state.get('entities', [])
    
    print(f"📅 Dates Found: {len(dates)}")
    if dates:
        for date in dates[:3]:
            print(f"   - {date.get('date')}: {date.get('context', 'N/A')[:60]}...")
    print()
    
    print(f"👥 People Identified: {len(people)}")
    if people:
        for person in people[:5]:
            print(f"   - {person.get('name')}: {person.get('role', 'N/A')}")
    print()
    
    print(f"🏢 Entities: {len(entities)}")
    if entities:
        for entity in entities[:5]:
            print(f"   - {entity.get('name')} ({entity.get('type')})")
    print()
    
    # Privilege Check
    privilege_flags = state.get('privilege_flags', [])
    print(f"🔒 Privilege Issues: {len(privilege_flags)}")
    if privilege_flags:
        for flag in privilege_flags[:3]:
            print(f"   - Type: {flag.get('type')}")
            print(f"     Reason: {flag.get('reasoning', 'N/A')[:80]}...")
            print(f"     Confidence: {flag.get('confidence', 0):.2%}")
    print()
    
    # Hot Doc Detection
    is_hot = state.get('is_hot_doc', False)
    hot_score = state.get('hot_doc_score', 0)
    hot_severity = state.get('hot_doc_severity', 'low')
    
    if is_hot:
        print(f"🔥 HOT DOCUMENT DETECTED!")
        print(f"   Score: {hot_score:.2f}/1.0")
        print(f"   Severity: {hot_severity.upper()}")
        
        hot_reasons = state.get('hot_doc_reasons', [])
        if hot_reasons:
            print(f"   Reasons:")
            for reason in hot_reasons[:2]:
                print(f"   - Type: {reason.get('type')}")
                print(f"     Excerpt: {reason.get('excerpt', 'N/A')[:100]}...")
                print(f"     Impact: {reason.get('impact', 'N/A')[:80]}...")
    else:
        print(f"   Not flagged as hot document (score: {hot_score:.2f})")
    print()
    
    # Summary
    summary = state.get('summary', '')
    if summary:
        print(f"📝 Summary:")
        print(f"   {summary[:300]}...")
    print()
    
    # Key Facts
    key_facts = state.get('key_facts', [])
    if key_facts:
        print(f"💡 Key Facts ({len(key_facts)}):")
        for fact in key_facts[:3]:
            print(f"   - {fact[:100]}...")
    print()
    
    # Legal Issues
    legal_issues = state.get('legal_issues', [])
    if legal_issues:
        print(f"⚖️  Legal Issues ({len(legal_issues)}):")
        for issue in legal_issues[:3]:
            print(f"   - {issue[:100]}...")
    print()
    
    # Errors
    errors = state.get('errors', [])
    if errors:
        print(f"❌ Errors: {len(errors)}")
        for error in errors:
            print(f"   - Agent: {error.get('agent')}")
            print(f"     Error: {error.get('error')[:80]}...")
    
    print(f"\n{'='*70}\n")


async def test_document(doc_type, document_text):
    """Test a single document through the pipeline"""
    print(f"\n🚀 Testing {doc_type.upper()} document...")
    print(f"   Length: {len(document_text)} characters")
    print(f"   Starting pipeline...\n")
    
    try:
        result = await run_pipeline(
            document_url=f"test://{doc_type}.txt",
            case_id="test-case-123",
            job_id=f"test-job-{doc_type}",
            raw_text=document_text,
            rag_retriever=None
        )
        
        format_result(doc_type, result)
        return result
        
    except Exception as e:
        print(f"❌ Error testing {doc_type}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🤖 CaseIntel AI Agents - Standalone Test")
    print("="*70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    # Test each document type
    results = {}
    
    # Test 1: Contract (should be straightforward)
    results['contract'] = await test_document('contract', TEST_DOCUMENTS['contract'])
    
    # Test 2: Privileged (should detect attorney-client privilege)
    results['privileged'] = await test_document('privileged', TEST_DOCUMENTS['privileged'])
    
    # Test 3: Smoking Gun (should be flagged as hot doc)
    results['smoking_gun'] = await test_document('smoking_gun', TEST_DOCUMENTS['smoking_gun'])
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print()
    
    for doc_type, result in results.items():
        if result:
            status = result.get('status', 'unknown')
            doc_class = result.get('document_type', 'N/A')
            is_hot = result.get('is_hot_doc', False)
            has_privilege = len(result.get('privilege_flags', [])) > 0
            
            print(f"{doc_type.upper()}: ")
            print(f"  Status: {status}")
            print(f"  Classification: {doc_class}")
            print(f"  Hot Doc: {'🔥 YES' if is_hot else 'No'}")
            print(f"  Privilege: {'🔒 YES' if has_privilege else 'No'}")
            print()
        else:
            print(f"{doc_type.upper()}: ❌ FAILED")
            print()
    
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
