#!/usr/bin/env python3
"""
Test AWS Bedrock connection with Claude 4.5 models.
Run this to verify your Bedrock setup is working correctly.
"""
import boto3
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_model(model_id: str, model_name: str):
    """Test a specific Bedrock model"""
    print(f"\n{'='*70}")
    print(f"Testing: {model_name}")
    print(f"Model ID: {model_id}")
    print(f"{'='*70}")
    
    try:
        client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        body = json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 100,
            'messages': [{
                'role': 'user',
                'content': 'Say "Hello from Claude 4.5!" and tell me which model you are in one sentence.'
            }]
        })
        
        response = client.invoke_model(
            modelId=model_id,
            body=body
        )
        
        result = json.loads(response['body'].read())
        response_text = result['content'][0]['text']
        
        print(f"✅ SUCCESS!")
        print(f"Response: {response_text}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED!")
        print(f"Error: {str(e)}")
        return False


def main():
    """Test all configured models"""
    print("\n" + "="*70)
    print("AWS BEDROCK CONNECTION TEST")
    print("Testing Claude 4.5 Models")
    print("="*70)
    
    # Check environment variables
    print("\n📋 Checking Environment Variables...")
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        sys.exit(1)
    
    print("✅ All required environment variables are set")
    print(f"   Region: {os.getenv('AWS_REGION')}")
    
    # Test models
    models_to_test = [
        (
            os.getenv('MODEL_HAIKU', 'anthropic.claude-haiku-4-5-20251001-v1:0'),
            'Claude Haiku 4.5 (Fast & Cost-Effective)'
        ),
        (
            os.getenv('MODEL_SONNET', 'anthropic.claude-sonnet-4-5-20250929-v1:0'),
            'Claude Sonnet 4.5 (Complex Reasoning)'
        ),
    ]
    
    results = []
    for model_id, model_name in models_to_test:
        success = test_model(model_id, model_name)
        results.append((model_name, success))
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    for model_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {model_name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print(f"\n🎉 All tests passed! Your Bedrock setup is working correctly.")
        print(f"\nYou can now run the CaseIntel AI Agents pipeline!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Please check your AWS Bedrock configuration.")
        print(f"\nTroubleshooting:")
        print(f"1. Verify model access in AWS Console → Bedrock → Model Access")
        print(f"2. Check IAM permissions include 'bedrock:InvokeModel'")
        print(f"3. Ensure AWS credentials are correct in .env file")
        sys.exit(1)


if __name__ == '__main__':
    main()
