# AWS App Runner Deployment Guide

## Cost Estimate: $7-10/month

**Breakdown:**
- Compute: 1 vCPU × 730 hours × $0.007 = $5.11
- Memory: 2GB × 730 hours × $0.0008 = $1.17
- Requests: ~100K/month × $0.10/million = $0.01
- **Total: ~$6.29/month** (plus minimal request costs)

---

## Prerequisites

1. AWS Account
2. GitHub repository with agents code
3. AWS CLI installed (optional but recommended)

---

## Step 1: Prepare Your Repository

### 1.1 Create `apprunner.yaml` (App Runner configuration)

```yaml
version: 1.0
runtime: python3
build:
  commands:
    pre-build:
      - pip install --upgrade pip
    build:
      - pip install -r requirements.txt
    post-build:
      - echo "Build complete"
run:
  runtime-version: 3.11
  command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
  env:
    - name: PYTHONUNBUFFERED
      value: "1"
```

### 1.2 Update `requirements.txt`

Make sure it includes all dependencies:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
boto3==1.29.7
chromadb==0.4.18
langchain==0.0.340
langgraph==0.0.20
pydantic==2.5.0
python-dotenv==1.0.0
requests==2.31.0
```

### 1.3 Create `.apprunner-ignore` (optional)

```
.git
.kiro
test_documents
tests
venv
*.pyc
__pycache__
.env
.env.local
*.md
```

---

## Step 2: Set Up Environment Variables

Create a `.env.production` file (don't commit this):

```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# ChromaDB
CHROMA_PERSIST_DIR=/tmp/chroma

# API Security
CASEINTEL_API_KEY=your_production_api_key

# S3 (for document storage)
S3_BUCKET_NAME=caseintel-documents
S3_REGION=us-east-1
```

---

## Step 3: Deploy to AWS App Runner

### Option A: AWS Console (Easiest)

1. **Go to AWS App Runner Console**
   - https://console.aws.amazon.com/apprunner

2. **Create Service**
   - Click "Create service"

3. **Source Configuration**
   - Repository type: **Source code repository**
   - Connect to GitHub (first time only)
   - Select your repository: `your-org/CaseIntel`
   - Branch: `main` or `feature/agents-phase-one`
   - Deployment trigger: **Automatic** (deploys on push)

4. **Build Configuration**
   - Configuration file: **Use a configuration file**
   - File: `apprunner.yaml`

5. **Service Configuration**
   - Service name: `caseintel-agents`
   - Virtual CPU: **1 vCPU**
   - Memory: **2 GB**
   - Port: **8000**

6. **Environment Variables**
   Add each variable from `.env.production`:
   - `DATABASE_URL` = `postgresql://...`
   - `AWS_REGION` = `us-east-1`
   - `AWS_ACCESS_KEY_ID` = `...`
   - `AWS_SECRET_ACCESS_KEY` = `...` (mark as secret)
   - `CASEINTEL_API_KEY` = `...` (mark as secret)
   - `S3_BUCKET_NAME` = `caseintel-documents`

7. **Auto Scaling**
   - Min instances: **1** (or 0 to scale to zero)
   - Max instances: **3**
   - Max concurrency: **100**

8. **Health Check**
   - Path: `/health`
   - Interval: 10 seconds
   - Timeout: 5 seconds
   - Unhealthy threshold: 3

9. **Review and Create**
   - Review settings
   - Click "Create & deploy"
   - Wait 5-10 minutes for deployment

10. **Get Your URL**
    - App Runner will provide a URL like:
    - `https://abc123.us-east-1.awsapprunner.com`

### Option B: AWS CLI (Faster for updates)

```bash
# 1. Create service configuration
cat > service-config.json << 'EOF'
{
  "ServiceName": "caseintel-agents",
  "SourceConfiguration": {
    "AuthenticationConfiguration": {
      "ConnectionArn": "arn:aws:apprunner:us-east-1:ACCOUNT:connection/github"
    },
    "AutoDeploymentsEnabled": true,
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/your-org/CaseIntel",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port 8000",
          "Port": "8000",
          "RuntimeEnvironmentVariables": {
            "DATABASE_URL": "postgresql://...",
            "AWS_REGION": "us-east-1",
            "CASEINTEL_API_KEY": "..."
          }
        }
      }
    }
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 3
  },
  "AutoScalingConfigurationArn": "arn:aws:apprunner:us-east-1:ACCOUNT:autoscalingconfiguration/DefaultConfiguration"
}
EOF

# 2. Create the service
aws apprunner create-service --cli-input-json file://service-config.json

# 3. Get service URL
aws apprunner describe-service --service-arn <service-arn> \
  --query 'Service.ServiceUrl' --output text
```

---

## Step 4: Configure Custom Domain (Optional)

1. **In App Runner Console**
   - Go to your service
   - Click "Custom domains"
   - Add domain: `agents.caseintel.io`

2. **In Your DNS Provider**
   - Add CNAME record:
   - Name: `agents`
   - Value: `<app-runner-url>`

3. **SSL Certificate**
   - App Runner automatically provisions SSL
   - Wait 5-10 minutes for DNS propagation

---

## Step 5: Update Backend to Use New URL

```typescript
// backend/caseintel-backend/.env
PYTHON_AGENTS_URL=https://abc123.us-east-1.awsapprunner.com
# Or with custom domain:
# PYTHON_AGENTS_URL=https://agents.caseintel.io
AGENTS_API_KEY=your_production_api_key
```

---

## Step 6: Test Deployment

```bash
# Health check
curl https://your-app-runner-url.awsapprunner.com/health

# Test analysis (with API key)
curl -X POST https://your-app-runner-url.awsapprunner.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "document_url": "https://s3.amazonaws.com/...",
    "case_id": "test-case-123"
  }'
```

---

## Monitoring & Logs

### View Logs
```bash
# AWS Console
# App Runner → Your Service → Logs

# Or AWS CLI
aws logs tail /aws/apprunner/caseintel-agents/service --follow
```

### Metrics to Watch
- **Request count** - Should be low initially
- **Response time** - Should be < 30s for analysis
- **Error rate** - Should be < 1%
- **CPU/Memory** - Should stay under 80%

---

## Cost Optimization Tips

### 1. Scale to Zero (Save ~$3/month)
```yaml
# In App Runner console
Auto Scaling:
  Min instances: 0  # Scale to zero when idle
  Max instances: 3
```
**Tradeoff**: First request after idle has 10-15s cold start

### 2. Use Spot Instances (Future)
- Not available in App Runner yet
- Consider ECS Fargate Spot for 70% savings

### 3. Optimize Memory
- Start with 2GB
- Monitor usage
- Reduce to 1GB if consistently under 50% usage
- **Savings**: ~$0.60/month

### 4. Request Batching
- Process multiple documents in one request
- Reduces per-request overhead

---

## Troubleshooting

### Issue: Deployment Fails

**Check:**
1. `requirements.txt` has all dependencies
2. `apprunner.yaml` syntax is correct
3. Environment variables are set
4. GitHub connection is active

**Fix:**
```bash
# View deployment logs
aws apprunner list-operations --service-arn <arn>
```

### Issue: Health Check Failing

**Check:**
1. `/health` endpoint returns 200
2. Port 8000 is correct
3. App is actually starting

**Fix:**
```python
# Ensure health endpoint exists
@router.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Issue: Database Connection Fails

**Check:**
1. `DATABASE_URL` is correct
2. Railway allows connections from AWS IPs
3. SSL mode is correct

**Fix:**
```python
# In src/services/db.py
connect_args = {
    "sslmode": "require",
    "connect_timeout": 10
}
```

### Issue: AWS Bedrock Access Denied

**Check:**
1. AWS credentials are correct
2. IAM role has Bedrock permissions
3. Region is correct (us-east-1)

**Fix:**
```json
// IAM Policy
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ],
    "Resource": "*"
  }]
}
```

---

## Migration Path (Future)

When you're ready to move everything to AWS:

### Phase 1: Agents on App Runner ✅ (Current)
- Python agents: AWS App Runner
- NestJS API: Railway
- PostgreSQL: Railway
- Frontend: Vercel

### Phase 2: Database to AWS RDS
- PostgreSQL: AWS RDS
- NestJS API: Railway
- Python agents: App Runner
- Frontend: Vercel

### Phase 3: API to AWS ECS
- PostgreSQL: AWS RDS
- NestJS API: AWS ECS Fargate
- Python agents: AWS ECS Fargate
- Frontend: Vercel

### Phase 4: Full AWS
- PostgreSQL: AWS RDS
- NestJS API: AWS ECS Fargate
- Python agents: AWS ECS Fargate
- Frontend: AWS Amplify or CloudFront + S3

---

## Next Steps

1. ✅ Deploy to App Runner
2. ✅ Test with production data
3. ✅ Monitor costs for first week
4. ✅ Integrate with NestJS backend
5. ✅ Update frontend to show results

Ready to deploy? Let me know if you need help with any step!
