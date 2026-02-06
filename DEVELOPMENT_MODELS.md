# 💰 Development Models Configuration

## Cost-Effective Setup for Development

You're using **Claude 3.5 Sonnet** and **Claude 3 Haiku** for development - this is a smart approach that can save you significant costs while building and testing!

## Your Development Models

### Models You've Enabled in AWS Bedrock

✅ **us.anthropic.claude-3-5-sonnet-20241022-v2:0** (Claude 3.5 Sonnet)
- Use for: Privilege checking, hot doc detection, content analysis
- Cost: $3.00 per 1M input tokens, $15.00 per 1M output tokens
- Quality: Excellent for legal analysis

✅ **anthropic.claude-3-haiku-20240307-v1:0** (Claude 3 Haiku)
- Use for: Classification, metadata extraction, cross-referencing
- Cost: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- Quality: Very good for structured tasks

✅ **amazon.titan-embed-text-v2:0** (Titan Embeddings)
- Use for: RAG vector embeddings
- Cost: $0.02 per 1M input tokens
- Quality: Excellent for semantic search

## Cost Comparison

### Development Setup (Your Current Config)

| Task | Model | Cost per 10K tokens |
|------|-------|---------------------|
| Classification | Claude 3 Haiku | $0.0025 |
| Metadata | Claude 3 Haiku | $0.0025 |
| Privilege | Claude 3.5 Sonnet | $0.03 |
| Hot Docs | Claude 3.5 Sonnet | $0.03 |
| Content | Claude 3.5 Sonnet | $0.03 |
| Cross-Ref | Claude 3 Haiku | $0.0025 |
| **Total per document** | | **~$0.10** |

### Production Setup (Claude 4.5)

| Task | Model | Cost per 10K tokens |
|------|-------|---------------------|
| Classification | Claude 4.5 Haiku | $0.0025 |
| Metadata | Claude 4.5 Haiku | $0.0025 |
| Privilege | Claude 4.5 Sonnet | $0.03 |
| Hot Docs | Claude 4.5 Sonnet | $0.03 |
| Content | Claude 4.5 Sonnet | $0.03 |
| Cross-Ref | Claude 4.5 Haiku | $0.0025 |
| **Total per document** | | **~$0.10** |

**Note**: Costs are similar because Claude 3.5 and 4.5 have the same pricing! The main difference is quality/capability.

## Configuration

Your `.env` file is now set up for development:

```bash
# Environment
ENVIRONMENT=development

# Development Models (Current)
MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0
MODEL_METADATA=anthropic.claude-3-haiku-20240307-v1:0
MODEL_PRIVILEGE=us.anthropic.claude-3-5-sonnet-20241022-v2:0
MODEL_HOTDOC=us.anthropic.claude-3-5-sonnet-20241022-v2:0
MODEL_CONTENT=us.anthropic.claude-3-5-sonnet-20241022-v2:0
MODEL_CROSSREF=anthropic.claude-3-haiku-20240307-v1:0

# Embeddings
EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
```

## When to Upgrade to Claude 4.5

Upgrade to Claude 4.5 when:

1. **Quality Matters More Than Cost**
   - Production deployment
   - Client-facing analysis
   - Critical legal decisions

2. **You Need Better Performance**
   - More accurate privilege detection
   - Better hot doc identification
   - More nuanced legal analysis

3. **You're Ready for Production**
   - Testing is complete
   - Budget is approved
   - Quality requirements are high

## How to Switch to Production Models

When you're ready, just update your `.env`:

```bash
# Change environment
ENVIRONMENT=production

# Comment out development models
# MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0
# ...

# Uncomment production models
MODEL_CLASSIFIER=anthropic.claude-haiku-4-5-20251001-v1:0
MODEL_METADATA=anthropic.claude-haiku-4-5-20251001-v1:0
MODEL_PRIVILEGE=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_HOTDOC=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_CONTENT=anthropic.claude-sonnet-4-5-20250929-v1:0
MODEL_CROSSREF=anthropic.claude-haiku-4-5-20251001-v1:0
```

No code changes needed - just restart the service!

## Quality Expectations

### Claude 3 Haiku vs Claude 4.5 Haiku
- **Speed**: Similar
- **Accuracy**: Claude 4.5 is ~10-15% better
- **Structured Output**: Claude 4.5 is more reliable
- **Cost**: Same

### Claude 3.5 Sonnet vs Claude 4.5 Sonnet
- **Reasoning**: Claude 4.5 is noticeably better
- **Legal Analysis**: Claude 4.5 is more nuanced
- **Context Understanding**: Claude 4.5 handles longer contexts better
- **Cost**: Same

## Testing Your Setup

Test your development models:

```bash
source venv/bin/activate
python scripts/test_bedrock.py
```

This will verify:
- ✅ AWS credentials are correct
- ✅ Models are accessible
- ✅ API calls work properly

## Cost Monitoring

### Track Your Development Costs

1. **AWS Cost Explorer**
   - Go to AWS Console → Cost Explorer
   - Filter by Service: "Amazon Bedrock"
   - Group by: Model ID

2. **Set Up Budget Alerts**
   ```bash
   # Example: Alert if costs exceed $10/day
   AWS Console → Budgets → Create Budget
   ```

3. **Monitor Usage**
   ```bash
   # CloudWatch metrics
   AWS Console → CloudWatch → Metrics → Bedrock
   ```

## Best Practices for Development

1. **Start with Small Documents**
   - Test with 1-2 page documents first
   - Verify quality before processing large batches

2. **Use Development Models for Testing**
   - Perfect for debugging and iteration
   - Switch to production models for final validation

3. **Monitor Quality vs Cost**
   - If Claude 3.5 quality is sufficient, keep using it
   - Upgrade specific agents to Claude 4.5 as needed

4. **Gradual Migration**
   - You can mix models! For example:
     ```bash
     # Keep cheap models for simple tasks
     MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0
     MODEL_METADATA=anthropic.claude-3-haiku-20240307-v1:0
     MODEL_CROSSREF=anthropic.claude-3-haiku-20240307-v1:0
     
     # Upgrade critical agents to Claude 4.5
     MODEL_PRIVILEGE=anthropic.claude-sonnet-4-5-20250929-v1:0
     MODEL_HOTDOC=anthropic.claude-sonnet-4-5-20250929-v1:0
     MODEL_CONTENT=anthropic.claude-sonnet-4-5-20250929-v1:0
     ```

## Embeddings: Amazon Titan

You're using **Amazon Titan Embed Text v2** for RAG embeddings:

- **Cost**: $0.02 per 1M tokens (very cheap!)
- **Dimensions**: 1024 (good for most use cases)
- **Quality**: Excellent for legal document search
- **Speed**: Very fast

### Alternative: Cohere Embeddings

If you need higher quality embeddings later:

```bash
EMBEDDING_MODEL=cohere.embed-english-v3
# Cost: $0.10 per 1M tokens (5x more expensive but higher quality)
```

## Summary

✅ **Your current setup is perfect for development!**

- Claude 3.5 Sonnet: Excellent quality for legal analysis
- Claude 3 Haiku: Great for structured extraction
- Amazon Titan: Cost-effective embeddings
- Same pricing as Claude 4.5 models
- Easy to upgrade when ready

## Next Steps

1. ✅ **Test your setup**
   ```bash
   python scripts/test_bedrock.py
   ```

2. ✅ **Process a test document**
   ```bash
   docker-compose up -d
   # Test with a small document
   ```

3. ✅ **Monitor costs**
   - Check AWS Cost Explorer daily
   - Set up budget alerts

4. ✅ **Evaluate quality**
   - If results are good, keep using Claude 3.5/3
   - If you need better quality, upgrade specific agents

5. ✅ **Switch to production when ready**
   - Update `.env` with Claude 4.5 models
   - Restart the service
   - No code changes needed!

---

**Development Status**: ✅ Configured for cost-effective development

You're all set to build and test without breaking the bank! 💰
