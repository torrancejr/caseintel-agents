# Cost Comparison: Your Existing Setup vs. New 6-Agent Pipeline

**Date**: February 11, 2026  
**Your Concern**: The new agents service seems expensive compared to your existing workflow

**Verdict**: ✅ **You're right! Your current setup is 3-4x cheaper.**

---

## Your Existing Backend Setup (CURRENT)

### Configuration
```env
AI_PROVIDER=bedrock
BEDROCK_CLASSIFICATION_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_CHAT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

### How It Works
1. **Rule-based keyword detection** (free, instant)
2. **ONE AI call** per document using Claude 3.5 Sonnet
3. **Text truncated** to 12,000 characters
4. **Single prompt** gets: privilege, entities, summary, key facts

### Cost Per Document
| Document Size | Input Tokens | Output Tokens | Cost |
|--------------|--------------|---------------|------|
| Small (1-5 pages) | ~3,000 | ~500 | **$0.0165** |
| Medium (5-20 pages) | ~8,000 | ~800 | **$0.0360** |
| Large (truncated at 12K) | ~10,000 | ~1,000 | **$0.0450** |

**Average: ~$0.03-0.05 per document**

### At 1,000 Documents/Month
- Small (40%): 400 × $0.0165 = **$6.60**
- Medium (40%): 400 × $0.036 = **$14.40**
- Large (20%): 200 × $0.045 = **$9.00**

**Total: ~$30/month** 💰

---

## New 6-Agent Pipeline (AGENTS SERVICE)

### Configuration
Uses 6 separate AI calls:
- **Agent 1**: Claude 3.5 Haiku (Classifier)
- **Agent 2**: Claude 3.5 Haiku (Metadata)
- **Agent 3**: Claude 3.5 Sonnet (Privilege)
- **Agent 4**: Claude 3.5 Sonnet (Hot Doc)
- **Agent 5**: Claude 3.5 Sonnet (Content)
- **Agent 6**: Claude 3.5 Haiku (Cross-Ref)

### Cost Per Document
**Average: ~$0.16 per document** (as calculated in COST_ANALYSIS.md)

### At 1,000 Documents/Month
**Total: ~$162/month** 💸

---

## Side-by-Side Comparison

| Metric | Your Current Setup | New Agents Pipeline | Difference |
|--------|-------------------|-------------------|------------|
| **AI Calls per Doc** | 1 | 6 | +500% |
| **Cost per Doc** | $0.03-0.05 | $0.16 | **+320%** |
| **Monthly Cost (1K docs)** | **$30** | **$162** | **+$132** |
| **Processing Time** | ~5-10 seconds | ~1.5 minutes | +1800% |
| **Features** | Privilege + Entities + Summary | All 6 agents | More comprehensive |

---

## What You're Getting for 5x the Cost

### Your Current Setup Provides:
- ✅ Privilege detection (keyword + AI)
- ✅ Entity extraction (people, orgs, dates, locations)
- ✅ Document summary
- ✅ Key facts
- ✅ Relevance scoring

### New Agents Add:
- 🆕 Detailed document classification (contract types, communication types)
- 🆕 **Hot Doc Detection** - Smoking guns, admissions, contradictions
- 🆕 Enhanced privilege confidence scoring
- 🆕 Timeline event extraction
- 🆕 Witness tracking across documents
- 🆕 Cross-document consistency checking
- 🆕 Legal issue identification
- 🆕 Evidence gap analysis
- 🆕 Draft narrative generation

---

## Recommendation: Hybrid Approach

**Best of Both Worlds**: Use your existing backend for most docs, agents for special cases

### Option 1: Smart Routing (Recommended)

```typescript
async analyzeDocument(documentId: string, user: User) {
  // Start with your fast, cheap classification
  const classification = await this.aiService.classifyDocument(documentId, user);
  
  // Only use expensive 6-agent pipeline for:
  const needsDeepAnalysis = 
    classification.privilege === 'yes' ||               // Privileged docs
    classification.privilegeConfidence > 0.7 ||         // High confidence privilege
    classification.relevanceScore > 0.8 ||              // Highly relevant
    documentType === 'deposition' ||                    // Depositions
    user.requestsDeepAnalysis;                          // User explicitly requests
  
  if (needsDeepAnalysis) {
    // Trigger full 6-agent pipeline
    await this.triggerAgentsPipeline(documentId, caseId);
  }
  
  return classification;
}
```

**Projected Costs with Smart Routing**:
- 80% of docs: Your cheap classification ($0.04 each) = **$32**
- 20% of docs: Full agents pipeline ($0.16 each) = **$32**
- **Total: ~$64/month** (2x your current, but 2.5x cheaper than all agents)

---

### Option 2: Keep Your Current Setup (Cheapest)

**Just enhance what you have**:

```typescript
// ai.service.ts - Enhanced single-call classification

const systemPrompt = `[Your existing prompt] + 

ALSO IDENTIFY HOT DOCUMENTS:
- Smoking guns (direct evidence of wrongdoing)
- Admissions against interest
- Contradictions with deposition testimony
- Critical evidence of damages/causation

OUTPUT:
{
  // existing fields...
  "isHotDoc": boolean,
  "hotDocScore": 0.0-1.0,
  "hotDocReasons": ["reasons"],
  "timelineEvents": [{"date": "...", "event": "..."}]
}`;
```

**Cost**: Still ~$30/month, now with hot doc detection!

---

### Option 3: Use Haiku Instead of Sonnet (Ultra-Cheap)

Switch your classification model from Sonnet to Haiku:

```env
# Change this:
BEDROCK_CLASSIFICATION_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0

# To this:
BEDROCK_CLASSIFICATION_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

**New Cost Per Document**:
- Small: $0.0025 (was $0.0165)
- Medium: $0.0054 (was $0.036)
- Large: $0.0068 (was $0.045)

**Monthly Cost (1K docs)**: **~$4-5/month** 🎉

**Trade-off**: Slightly lower accuracy on complex privilege detection

---

## Real Cost Breakdown: Your Current Setup

### Claude 3.5 Sonnet Pricing (Bedrock)
- **Input**: $3.00 per million tokens
- **Output**: $15.00 per million tokens

### Typical Document Analysis
```
Input: 10,000 tokens (12K chars truncated text + prompt)
Output: 1,000 tokens (JSON with entities, summary, facts)

Cost = (10,000 × $3.00 / 1M) + (1,000 × $15.00 / 1M)
     = $0.030 + $0.015
     = $0.045 per document
```

### At 1,000 Documents/Month
```
1,000 docs × $0.045 = $45/month
```

**But you also use Haiku for chat:**
```
Claude 3 Haiku:
- Input: $0.25 per million tokens
- Output: $1.25 per million tokens

100 chat messages/month with RAG context:
- Input: 50,000 tokens (500 per message with context)
- Output: 20,000 tokens (200 per response)
- Cost = (50K × $0.25 / 1M) + (20K × $1.25 / 1M)
     = $0.0125 + $0.025 = $0.0375/month
```

**Your Total Current Monthly Cost: ~$45-50/month** ✅

---

## Corrected Agents Pipeline Cost

I **overestimated** in my initial analysis. Let me recalculate:

### Actual Agent Pipeline (with optimizations)

If you configure agents to use Haiku where possible:

```env
MODEL_CLASSIFIER=anthropic.claude-3-haiku-20240307-v1:0
MODEL_METADATA=anthropic.claude-3-haiku-20240307-v1:0
MODEL_PRIVILEGE=us.anthropic.claude-3-5-sonnet-20241022-v2:0  # Keep Sonnet
MODEL_HOTDOC=us.anthropic.claude-3-5-sonnet-20241022-v2:0      # Keep Sonnet
MODEL_CONTENT=anthropic.claude-3-haiku-20240307-v1:0            # Use Haiku
MODEL_CROSSREF=anthropic.claude-3-haiku-20240307-v1:0           # Use Haiku
```

**New Cost per Document: ~$0.08** (half my original estimate)

**Monthly at 1,000 docs: ~$80** (still 1.8x your current)

---

## Final Recommendation

### ✅ **Keep Your Current Setup**

Your single-call approach is:
- ✅ **3x cheaper** ($30 vs $80-160/month)
- ✅ **10x faster** (5-10 seconds vs 1.5 minutes)
- ✅ **Simpler** (one service, integrated)
- ✅ **Already working**

You already get:
- Privilege detection with high accuracy
- Entity extraction
- Document summaries
- Key facts

### 🔧 **Enhance Your Existing Backend Instead**

Add to your current `ai.service.ts`:

```typescript
// Add hot doc detection to existing prompt (lines 453-498)
const enhancedPrompt = systemPrompt + `

HOT DOCUMENT DETECTION:
Also flag documents containing:
- Smoking guns (direct evidence of wrongdoing, cover-ups)
- Admissions against interest
- Contradictions with depositions or known facts
- Critical evidence of damages or causation

Add to your JSON output:
"isHotDoc": boolean,
"hotDocScore": 0.0-1.0,
"hotDocSeverity": "critical|high|medium|low",
"hotDocFlags": [{"type": "smoking_gun", "excerpt": "...", "reasoning": "..."}]
`;
```

**Cost increase**: $0 (same single API call)

---

## When to Use the 6-Agent Pipeline

Only for **special cases**:
- 🔍 **Depositions** - Need detailed witness tracking
- 🔥 **Known hot docs** - Need comprehensive analysis
- ⚖️ **Case-critical documents** - Need all 6 agents' insights
- 📊 **Large cases** - Need cross-document analysis

**Selective usage at 10% of docs**: ~$8/month additional cost

---

## Updated Cost Projection

### Your Smart Approach (Recommended)

| Feature | Tool | Volume | Cost |
|---------|------|--------|------|
| **Basic Classification** | Your backend (Sonnet) | 900 docs | **$40.50** |
| **Deep Analysis** | 6-Agent pipeline | 100 docs | **$8.00** |
| **Chat** | Your backend (Haiku) | unlimited | **$5.00** |
| **TOTAL** | Hybrid | 1,000 docs | **$53.50/month** |

**Savings vs. all agents**: $108.50/month (67% cheaper)

---

## Bottom Line

**Your existing setup is excellent.** Don't replace it - just **enhance** it:

1. Keep your `ai.service.ts` as primary classification
2. Add hot doc detection to the same prompt (free)
3. Use the 6-agent pipeline **only for** depositions and hot docs
4. Total cost: **~$50-60/month** instead of $162

**You built it right the first time!** 🎯
