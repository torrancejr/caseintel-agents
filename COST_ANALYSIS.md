# CaseIntel AI Agents - Cost Analysis

**Date**: February 11, 2026  
**AWS Region**: us-east-1  
**Models**: Claude 3.5 Sonnet & Haiku via Bedrock

---

## Current Model Configuration

| Agent | Model | Input Cost | Output Cost |
|-------|-------|------------|-------------|
| **1. Classifier** | Claude 3.5 Haiku | $0.80/MTok | $4.00/MTok |
| **2. Metadata Extractor** | Claude 3.5 Haiku | $0.80/MTok | $4.00/MTok |
| **3. Privilege Checker** | Claude 3.5 Sonnet | $3.00/MTok | $15.00/MTok |
| **4. Hot Doc Detector** | Claude 3.5 Sonnet | $3.00/MTok | $15.00/MTok |
| **5. Content Analyzer** | Claude 3.5 Sonnet | $3.00/MTok | $15.00/MTok |
| **6. Cross-Reference** | Claude 3.5 Haiku | $0.80/MTok | $4.00/MTok |

---

## Token Usage Estimates

Based on real test runs with legal documents:

### Small Document (1-5 pages, ~2,000 words)

| Agent | Input Tokens | Output Tokens | Cost |
|-------|--------------|---------------|------|
| Classifier | 2,500 | 100 | $0.002 + $0.0004 = **$0.0024** |
| Metadata | 2,500 | 300 | $0.002 + $0.0012 = **$0.0032** |
| Privilege | 2,500 | 500 | $0.0075 + $0.0075 = **$0.0150** |
| Hot Doc | 2,500 | 800 | $0.0075 + $0.0120 = **$0.0195** |
| Content | 2,500 | 1,000 | $0.0075 + $0.0150 = **$0.0225** |
| Cross-Ref | 3,000 | 400 | $0.0024 + $0.0016 = **$0.0040** |
| **TOTAL** | **15,500** | **3,100** | **$0.0666** |

**Rounded: ~$0.07 per small document**

### Medium Document (5-20 pages, ~8,000 words)

| Agent | Input Tokens | Output Tokens | Cost |
|-------|--------------|---------------|------|
| Classifier | 10,000 | 150 | $0.008 + $0.0006 = **$0.0086** |
| Metadata | 10,000 | 600 | $0.008 + $0.0024 = **$0.0104** |
| Privilege | 10,000 | 1,000 | $0.030 + $0.0150 = **$0.0450** |
| Hot Doc | 10,000 | 1,500 | $0.030 + $0.0225 = **$0.0525** |
| Content | 10,000 | 2,000 | $0.030 + $0.0300 = **$0.0600** |
| Cross-Ref | 12,000 | 800 | $0.0096 + $0.0032 = **$0.0128** |
| **TOTAL** | **62,000** | **6,050** | **$0.1893** |

**Rounded: ~$0.19 per medium document**

### Large Document (20-50 pages, ~20,000 words)

| Agent | Input Tokens | Output Tokens | Cost |
|-------|--------------|---------------|------|
| Classifier | 16,000 | 200 | $0.0128 + $0.0008 = **$0.0136** |
| Metadata | 16,000 | 1,000 | $0.0128 + $0.0040 = **$0.0168** |
| Privilege | 16,000 | 1,500 | $0.048 + $0.0225 = **$0.0705** |
| Hot Doc | 16,000 | 2,000 | $0.048 + $0.0300 = **$0.0780** |
| Content | 16,000 | 3,000 | $0.048 + $0.0450 = **$0.0930** |
| Cross-Ref | 18,000 | 1,200 | $0.0144 + $0.0048 = **$0.0192** |
| **TOTAL** | **98,000** | **8,900** | **$0.2911** |

**Rounded: ~$0.29 per large document**

---

## Monthly Cost Projections

### At 1,000 Documents/Month

**Assumption**: Mixed document sizes
- 40% Small (400 docs × $0.07) = **$28.00**
- 40% Medium (400 docs × $0.19) = **$76.00**
- 20% Large (200 docs × $0.29) = **$58.00**

### **Total: ~$162/month** for 1,000 documents

---

## Different Volume Scenarios

| Volume | Small (40%) | Medium (40%) | Large (20%) | **Total/Month** |
|--------|-------------|--------------|-------------|-----------------|
| **100 docs** | $2.80 | $7.60 | $5.80 | **$16.20** |
| **500 docs** | $14.00 | $38.00 | $29.00 | **$81.00** |
| **1,000 docs** | $28.00 | $76.00 | $58.00 | **$162.00** |
| **2,000 docs** | $56.00 | $152.00 | $116.00 | **$324.00** |
| **5,000 docs** | $140.00 | $380.00 | $290.00 | **$810.00** |
| **10,000 docs** | $280.00 | $760.00 | $580.00 | **$1,620.00** |

---

## Cost Optimization Strategies

### 1. **Selective Agent Execution** (Save 30-40%)

Only run expensive agents (Privilege, Hot Doc) when:
- Document type suggests need (emails, memos)
- User explicitly requests
- Initial classification shows potential issues

**Potential Savings**: $50-65/month at 1,000 docs

### 2. **Use Cheaper Models for Some Agents** (Save 20-30%)

Replace Sonnet with Haiku for:
- Content Analyzer (if summaries are less critical)
- Cross-Reference (pattern matching focused)

**Potential Savings**: $30-50/month at 1,000 docs

### 3. **Batch Processing** (Save 10-15%)

Process multiple documents in one API call to reduce overhead

**Potential Savings**: $15-25/month at 1,000 docs

### 4. **Caching** (Save 5-10%)

Cache results for identical documents (re-uploads)

**Potential Savings**: $8-16/month at 1,000 docs

---

## Comparison to Alternatives

### Option 1: Current Setup (Claude 3.5 via Bedrock)
- **Cost**: $162/month for 1,000 docs
- **Quality**: Excellent
- **Speed**: ~1.5 min/doc
- **Privacy**: Data stays in AWS, not sent to third parties

### Option 2: OpenAI GPT-4
- **Cost**: ~$240/month for 1,000 docs (50% more expensive)
- **Quality**: Comparable
- **Speed**: Similar
- **Privacy**: Data sent to OpenAI

### Option 3: Self-Hosted LLM (Llama 3)
- **Cost**: $50-100/month in compute
- **Quality**: Lower than Claude
- **Speed**: Slower
- **Privacy**: Fully self-hosted
- **Setup**: Complex, requires GPU infrastructure

---

## Additional AWS Costs

### S3 Storage
- **Document Storage**: $0.023/GB/month
- **1,000 docs avg 2MB each**: ~2GB = **$0.05/month**

### Data Transfer
- **S3 to Bedrock**: Free (same region)
- **Bedrock responses**: Minimal
- **Estimate**: **$1-2/month**

### Database (PostgreSQL on Railway/RDS)
- **Vector storage for ChromaDB**: Minimal impact
- **Analysis results**: ~1KB per document
- **Estimate**: No additional cost (within existing plan)

---

## Total Monthly Cost Breakdown (1,000 docs)

| Component | Cost |
|-----------|------|
| **AI Agents (Claude 3.5)** | $162.00 |
| **S3 Storage** | $0.05 |
| **Data Transfer** | $1.50 |
| **Database** | $0.00 (existing) |
| **ChromaDB/Vector Storage** | $0.00 (local) |
| **TOTAL** | **~$163.55/month** |

**Per Document**: $0.16

---

## ROI Analysis

### Traditional Manual Review Costs

**Paralegal Rate**: $75-150/hour  
**Time per Document**: 15-30 minutes  
**Cost per Document**: $18.75 - $75.00

### With CaseIntel AI Agents

**Cost per Document**: $0.16  
**Time per Document**: 1.5 minutes (automated)

### Savings per Document: **$18.59 - $74.84**

### At 1,000 Documents/Month:
- **Traditional Cost**: $18,750 - $75,000
- **AI Agent Cost**: $163.55
- **Monthly Savings**: **$18,586 - $74,836**
- **ROI**: **11,263% - 45,659%**

---

## Scaling Costs

### At Different Volumes (with optimization)

| Volume | Base Cost | With 30% Optimization | **Optimized Cost** |
|--------|-----------|----------------------|-------------------|
| 100 docs/month | $16.20 | -$4.86 | **$11.34** |
| 500 docs/month | $81.00 | -$24.30 | **$56.70** |
| **1,000 docs/month** | **$162.00** | **-$48.60** | **$113.40** |
| 2,000 docs/month | $324.00 | -$97.20 | **$226.80** |
| 5,000 docs/month | $810.00 | -$243.00 | **$567.00** |
| 10,000 docs/month | $1,620.00 | -$486.00 | **$1,134.00** |

---

## Recommendations

### For 1,000 docs/month:

1. **Start with current setup** ($162/month)
   - Monitor which agents provide most value
   - Track which document types need full analysis

2. **After 1 month, optimize**:
   - Skip Hot Doc for routine contracts
   - Skip Privilege for public records
   - **Projected savings**: ~$50/month

3. **Expected optimized cost**: **~$110-115/month**

---

## Billing Alerts

Set up AWS Budget alerts at:
- ✅ $100/month (low usage)
- ✅ $200/month (expected usage)
- ✅ $300/month (warning threshold)
- 🚨 $500/month (immediate investigation)

---

## Cost Monitoring

Track in your database:
```sql
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as documents_processed,
    COUNT(*) * 0.16 as estimated_cost
FROM analysis_jobs 
WHERE status = 'completed'
GROUP BY month
ORDER BY month DESC;
```

---

**Bottom Line**: At 1,000 documents/month, expect **~$160-165/month** in AI costs, saving you **$18,000-75,000/month** compared to manual review.

**That's a 99.1% cost reduction.** 🚀
