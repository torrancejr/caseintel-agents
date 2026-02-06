# AWS Bedrock Setup Guide

This project uses AWS Bedrock to access Claude models instead of the direct Anthropic API. This gives you better cost control and the ability to use different models for different tasks.

## Why Bedrock?

- **Cost Optimization**: Use cheaper Haiku models for simple tasks, Sonnet for complex reasoning
- **AWS Integration**: Seamless integration with your AWS infrastructure
- **Centralized Billing**: All AI costs in one AWS account
- **Enterprise Features**: VPC endpoints, CloudWatch logging, IAM policies

## Model Strategy

We use different Claude models for different agents based on task complexity:

### Haiku (Fast & Cost-Effective)
- **Document Classifier** - Simple pattern matching
- **Metadata Extractor** - Structured data extraction
- **Cross-Reference Engine** - Document matching and retrieval

### Sonnet (Complex Reasoning)
- **Privilege Checker** - Nuanced legal analysis
- **Hot Doc Detector** - Critical judgment calls
- **Content Analyzer** - Sophisticated summarization

## Setup Steps

### 1. Enable Bedrock Models

1. Go to AWS Console → Bedrock → Model Access
2. Request access to these models:
   - `anthropic.claude-haiku-4-20250514-v1:0`
   - `anthropic.claude-sonnet-4-20250514-v1:0`
3. Wait for approval (usually instant)

### 2. Create IAM User/Role

Create an IAM policy with Bedrock permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::caseintel-documents/*"
      ]
    }
  ]
}
```

### 3. Configure Environment Variables

Update your `.env` file:

```bash
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET=caseintel-documents

# Model IDs for different agents
MODEL_CLASSIFIER=anthropic.claude-haiku-4-20250514-v1:0
MODEL_METADATA=anthropic.claude-haiku-4-20250514-v1:0
MODEL_PRIVILEGE=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_HOTDOC=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_CONTENT=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_CROSSREF=anthropic.claude-haiku-4-20250514-v1:0
```

### 4. Test the Connection

```bash
# Activate virtual environment
source venv/bin/activate

# Test Bedrock connection
python -c "
import boto3
import json

client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.invoke_model(
    modelId='anthropic.claude-haiku-4-20250514-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 100,
        'messages': [{'role': 'user', 'content': 'Hello!'}]
    })
)
result = json.loads(response['body'].read())
print('✅ Bedrock connection successful!')
print(result['content'][0]['text'])
"
```

## Cost Comparison

Approximate costs per 1M tokens (as of 2025):

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| **Haiku** | $0.25 | $1.25 | Classification, extraction, matching |
| **Sonnet** | $3.00 | $15.00 | Complex analysis, reasoning, judgment |

**Example Cost Savings:**
- Using Haiku for 3 agents instead of Sonnet: **~90% cost reduction** on those tasks
- Typical document (10K tokens): **$0.15** with mixed models vs **$0.45** with all Sonnet

## Model Configuration

You can customize which model each agent uses by setting environment variables:

```bash
# Use Sonnet for everything (higher quality, higher cost)
MODEL_CLASSIFIER=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_METADATA=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_PRIVILEGE=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_HOTDOC=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_CONTENT=anthropic.claude-sonnet-4-20250514-v1:0
MODEL_CROSSREF=anthropic.claude-sonnet-4-20250514-v1:0

# Or use Haiku for everything (lower cost, still good quality)
MODEL_CLASSIFIER=anthropic.claude-haiku-4-20250514-v1:0
MODEL_METADATA=anthropic.claude-haiku-4-20250514-v1:0
MODEL_PRIVILEGE=anthropic.claude-haiku-4-20250514-v1:0
MODEL_HOTDOC=anthropic.claude-haiku-4-20250514-v1:0
MODEL_CONTENT=anthropic.claude-haiku-4-20250514-v1:0
MODEL_CROSSREF=anthropic.claude-haiku-4-20250514-v1:0
```

## Monitoring Costs

### CloudWatch Metrics

Bedrock automatically logs usage to CloudWatch:

1. Go to CloudWatch → Metrics → Bedrock
2. View metrics by model ID
3. Set up alarms for cost thresholds

### Cost Explorer

1. Go to AWS Cost Explorer
2. Filter by Service: "Amazon Bedrock"
3. Group by: Model ID
4. View daily/monthly costs

## Troubleshooting

### "Model not found" Error

**Problem**: Model ID not available in your region

**Solution**: 
- Check model availability: https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html
- Use `us-east-1` or `us-west-2` for best model availability

### "Access Denied" Error

**Problem**: IAM permissions not configured

**Solution**:
1. Check IAM policy includes `bedrock:InvokeModel`
2. Verify model ARN in policy matches your region
3. Ensure AWS credentials are correctly set

### "Throttling" Error

**Problem**: Too many requests

**Solution**:
- Request quota increase in Service Quotas console
- Implement exponential backoff (already included in base agent)
- Consider using multiple AWS accounts for higher throughput

## Migration from Direct Anthropic API

If you were using the direct Anthropic API before:

1. **No code changes needed** - The base agent handles both
2. **Remove** `ANTHROPIC_API_KEY` from `.env`
3. **Add** AWS credentials and model IDs
4. **Test** with a single document first
5. **Monitor** costs in AWS Cost Explorer

## Best Practices

1. **Start with recommended model split** (Haiku for simple, Sonnet for complex)
2. **Monitor costs** for first week to understand usage patterns
3. **Adjust model assignments** based on quality vs cost tradeoff
4. **Use CloudWatch alarms** to prevent unexpected costs
5. **Test in development** before deploying to production

## Support

- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **Claude on Bedrock**: https://docs.anthropic.com/claude/docs/claude-on-amazon-bedrock
- **Pricing**: https://aws.amazon.com/bedrock/pricing/

## Next Steps

1. ✅ Enable Bedrock models in AWS Console
2. ✅ Create IAM user/role with permissions
3. ✅ Update `.env` with AWS credentials
4. ✅ Test connection with sample script
5. ✅ Run your first document analysis
6. ✅ Monitor costs in CloudWatch

You're all set to use AWS Bedrock with CaseIntel AI Agents! 🚀
