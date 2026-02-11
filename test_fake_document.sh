#!/bin/bash

# Test CaseIntel Agents with Fake Documents
# This script tests the full pipeline without requiring S3 or real database records

API_URL="http://localhost:8000"
API_KEY="4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6"

# Use valid UUIDs
CASE_ID="123e4567-e89b-12d3-a456-426614174000"

echo "============================================"
echo "CaseIntel Agents - Fake Document Test"
echo "============================================"
echo ""

# Test 1: Simple Contract (should classify as contract, low privilege risk)
echo "📄 Test 1: Analyzing Fake Contract..."
echo ""

JOB1=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"case_id\": \"$CASE_ID\",
    \"document_text\": \"SERVICE AGREEMENT\\n\\nThis Service Agreement (\\\"Agreement\\\") is entered into as of January 15, 2026, by and between:\\n\\nAcme Corporation (\\\"Provider\\\")\\n123 Business St, New York, NY 10001\\n\\nand\\n\\nGlobal Industries Inc. (\\\"Client\\\")\\n456 Commerce Ave, Los Angeles, CA 90001\\n\\nWHEREAS, Provider agrees to provide consulting services as outlined in Schedule A;\\n\\nWHEREAS, Client agrees to pay the fees as specified in Section 3.\\n\\nNOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:\\n\\n1. SERVICES\\nProvider shall provide business consulting services to Client as detailed in the attached Schedule A.\\n\\n2. TERM\\nThis Agreement shall commence on February 1, 2026 and continue for twelve (12) months.\\n\\n3. COMPENSATION\\nClient shall pay Provider $10,000 per month, due on the first day of each month.\\n\\n4. CONFIDENTIALITY\\nBoth parties agree to maintain confidentiality of proprietary information.\\n\\n5. TERMINATION\\nEither party may terminate this Agreement with 30 days written notice.\\n\\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.\\n\\nSigned: John Smith, CEO, Acme Corporation\\nSigned: Jane Doe, President, Global Industries Inc.\"
  }")

JOB1_ID=$(echo $JOB1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'ERROR'))")

if [ "$JOB1_ID" = "ERROR" ]; then
    echo "❌ Test 1 Failed to create job"
    echo $JOB1 | python3 -m json.tool
else
    echo "✅ Test 1 Job Created: $JOB1_ID"
    echo "   Waiting for processing..."
    sleep 5
    
    # Check status
    STATUS=$(curl -s "$API_URL/api/v1/status/$JOB1_ID" -H "X-API-Key: $API_KEY")
    echo $STATUS | python3 -m json.tool
fi

echo ""
echo "============================================"
echo ""

# Test 2: Privileged Email (should detect attorney-client privilege)
echo "🔒 Test 2: Analyzing Privileged Attorney Email..."
echo ""

JOB2=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"case_id\": \"$CASE_ID\",
    \"document_text\": \"CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION\\n\\nFrom: sarah.johnson@lawfirm.com\\nTo: john.smith@acmecorp.com\\nDate: January 20, 2026\\nSubject: Re: Product Liability Strategy - PRIVILEGED\\n\\nDear John,\\n\\nThank you for meeting with me yesterday regarding the brake pad defect litigation.\\n\\nAs your legal counsel, I must advise you of the following:\\n\\n1. ATTORNEY WORK PRODUCT\\nOur analysis shows that the internal emails from March 2025 discussing the known brake defects are highly problematic. The email where your VP of Engineering stated \\\"we should recall but it will cost too much\\\" is particularly damaging.\\n\\n2. PRIVILEGE PROTECTION\\nWe need to immediately assert attorney-client privilege over all communications regarding this matter. Please do NOT discuss this with anyone outside of legal counsel.\\n\\n3. LITIGATION STRATEGY\\nI recommend we:\\n- File a motion to seal the March 2025 emails\\n- Prepare for settlement negotiations\\n- Conduct privilege review of all engineering documents\\n\\nThis communication contains attorney work product and is protected by attorney-client privilege. Do not forward or disclose.\\n\\nBest regards,\\nSarah Johnson, Esq.\\nPartner, Smith & Johnson LLP\\nAttorney for Acme Corporation\"
  }")

JOB2_ID=$(echo $JOB2 | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'ERROR'))")

if [ "$JOB2_ID" = "ERROR" ]; then
    echo "❌ Test 2 Failed to create job"
    echo $JOB2 | python3 -m json.tool
else
    echo "✅ Test 2 Job Created: $JOB2_ID"
    echo "   Waiting for processing..."
    sleep 5
    
    # Check status
    STATUS=$(curl -s "$API_URL/api/v1/status/$JOB2_ID" -H "X-API-Key: $API_KEY")
    echo $STATUS | python3 -m json.tool
fi

echo ""
echo "============================================"
echo ""

# Test 3: Smoking Gun Email (should be flagged as hot doc)
echo "🔥 Test 3: Analyzing Smoking Gun Document..."
echo ""

JOB3=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"case_id\": \"$CASE_ID\",
    \"document_text\": \"From: mike.peterson@acmecorp.com\\nTo: lisa.chen@acmecorp.com\\nDate: March 15, 2025\\nSubject: Brake Pad Testing Results - URGENT\\n\\nLisa,\\n\\nI just reviewed the Q1 testing data and we have a MAJOR problem.\\n\\nThe new brake pads are failing stress tests at 60% of expected lifespan. This means they could fail catastrophically in real-world conditions, especially in emergency braking situations.\\n\\nI know we're scheduled to ship 50,000 units next month, but we CANNOT release these. People could die.\\n\\nI brought this up in yesterday's meeting and was told \\\"the recall cost would exceed our quarterly profit target.\\\" When I pressed the issue, Tom said \\\"just make sure this email doesn't leak.\\\"\\n\\nI'm documenting this for the record. We KNOW these brakes are defective. We KNOW they pose a safety risk. And we're choosing profit over safety.\\n\\nIf someone gets hurt, this is on management. I tried to stop it.\\n\\nI'm copying this to my personal email as backup.\\n\\nMike Peterson\\nSenior QA Engineer\\nAcme Corporation\"
  }")

JOB3_ID=$(echo $JOB3 | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'ERROR'))")

if [ "$JOB3_ID" = "ERROR" ]; then
    echo "❌ Test 3 Failed to create job"
    echo $JOB3 | python3 -m json.tool
else
    echo "✅ Test 3 Job Created: $JOB3_ID"
    echo "   Waiting for processing..."
    sleep 5
    
    # Check status
    STATUS=$(curl -s "$API_URL/api/v1/status/$JOB3_ID" -H "X-API-Key: $API_KEY")
    echo $STATUS | python3 -m json.tool
fi

echo ""
echo "============================================"
echo ""

# Test 4: Deposition Transcript (metadata extraction test)
echo "📝 Test 4: Analyzing Deposition Transcript..."
echo ""

JOB4=$(curl -s -X POST $API_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"case_id\": \"$CASE_ID\",
    \"document_text\": \"DEPOSITION OF MICHAEL PETERSON\\n\\nIn the matter of:\\nSmith v. Acme Corporation\\nCase No. 2025-CV-12345\\n\\nDate: December 10, 2025\\nLocation: Law Offices of Johnson & Associates, New York, NY\\n\\nAppearances:\\nFor Plaintiff: Robert Johnson, Esq.\\nFor Defendant: Sarah Wilson, Esq.\\n\\nWITNESS: Michael Peterson, sworn\\n\\nQ: Please state your name and occupation for the record.\\nA: Michael Peterson. I'm a Senior QA Engineer at Acme Corporation.\\n\\nQ: How long have you worked at Acme?\\nA: Five years, since January 2020.\\n\\nQ: Were you involved in testing the brake pads that are the subject of this lawsuit?\\nA: Yes, I was the lead QA engineer on that project.\\n\\nQ: When did you first become aware of safety concerns with the brake pads?\\nA: In March 2025, during our quarterly testing cycle.\\n\\nQ: What did the testing reveal?\\nA: The brake pads were failing stress tests. They showed only 60% of the expected lifespan.\\n\\nQ: Did you report these findings?\\nA: Yes, immediately. I sent an email to Lisa Chen, my supervisor, and brought it up in our weekly team meeting.\\n\\nQ: What was management's response?\\nA: They told me the recall would be too expensive. Tom Davidson, our VP, said we should proceed with the shipment.\\n\\nQ: Did anyone tell you to keep this quiet?\\nA: Yes. Tom said, and I quote, \\\"make sure this email doesn't leak.\\\"\\n\\nQ: Did you have any concerns about proceeding?\\nA: Absolutely. I told them people could get hurt. These brakes could fail in emergency situations.\\n\\nQ: But they shipped them anyway?\\nA: Yes. Over my objections.\\n\\nQ: Thank you, Mr. Peterson. No further questions.\"
  }")

JOB4_ID=$(echo $JOB4 | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'ERROR'))")

if [ "$JOB4_ID" = "ERROR" ]; then
    echo "❌ Test 4 Failed to create job"
    echo $JOB4 | python3 -m json.tool
else
    echo "✅ Test 4 Job Created: $JOB4_ID"
    echo "   Waiting for processing..."
    sleep 5
    
    # Check status
    STATUS=$(curl -s "$API_URL/api/v1/status/$JOB4_ID" -H "X-API-Key: $API_KEY")
    echo $STATUS | python3 -m json.tool
fi

echo ""
echo "============================================"
echo "📊 Test Summary"
echo "============================================"
echo ""
echo "Job IDs for checking results:"
echo "  Test 1 (Contract): $JOB1_ID"
echo "  Test 2 (Privileged): $JOB2_ID"
echo "  Test 3 (Hot Doc): $JOB3_ID"
echo "  Test 4 (Deposition): $JOB4_ID"
echo ""
echo "Check individual results:"
echo "  curl -s $API_URL/api/v1/status/JOB_ID -H 'X-API-Key: $API_KEY' | python3 -m json.tool"
echo ""
echo "View detailed results:"
echo "  curl -s $API_URL/api/v1/results/JOB_ID -H 'X-API-Key: $API_KEY' | python3 -m json.tool"
echo ""
