# AWS App Runner Deployment Checklist

## Pre-Deployment

### 1. Verify Local Setup ✅
- [x] All tests passing locally
- [x] API running on `localhost:8000`
- [x] Database connection working
- [x] AWS Bedrock access configured

### 2. Prepare Repository
- [ ] Push latest code to GitHub
- [ ] Verify `apprunner.yaml` exists
- [ ] Verify `requirements.txt` is complete
- [ ] Verify `.apprunnerignore` exists

### 3. Gather Environment Variables

Copy these from your local `.env` file:

```bash
# From agents/.env
DATABASE_URL=postgresql://...
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
CASEINTEL_API_KEY=...
S3_BUCKET_NAME=caseintel-documents
S3_REGION=us-east-1
```

---

## Deployment Steps

### Step 1: Push to GitHub

```bash
cd agents
git add apprunner.yaml .apprunnerignore .env.production.example
git commit -m "feat: add AWS App Runner deployment configuration"
git push origin feature/agents-phase-one
```

### Step 2: AWS Console Setup

1. **Go to AWS App Runner**
   - URL: https://console.aws.amazon.com/apprunner
   - Region: **us-east-1** (recommended)

2. **Create Service**
   - Click "Create service"

3. **Source and Deployment**
   - Repository type: **Source code repository**
   - Provider: **GitHub**
   - Click "Add new" to connect GitHub (first time only)
   - Authorize AWS App Runner to access your repos

4. **Repository Settings**
   - Repository: Select your CaseIntel repo
   - Branch: `feature/agents-phase-one` (or `main`)
   - Deployment trigger: **Automatic**
   - Click "Next"

5. **Build Settings**
   - Configuration file: **Use a configuration file**
   - Configuration file path: `agents/apprunner.yaml`
   - Click "Next"

6. **Service Settings**
   - Service name: `caseintel-agents`
   - Virtual CPU: **1 vCPU**
   - Memory: **2 GB**
   - Port: **8000**

7. **Environment Variables** (Click "Add environment variable" for each)

   | Name | Value | Secret? |
   |------|-------|---------|
   | `DATABASE_URL` | `postgresql://...` | ✅ Yes |
   | `AWS_REGION` | `us-east-1` | No |
   | `AWS_ACCESS_KEY_ID` | `AKIA...` | ✅ Yes |
   | `AWS_SECRET_ACCESS_KEY` | `...` | ✅ Yes |
   | `CASEINTEL_API_KEY` | `...` | ✅ Yes |
   | `S3_BUCKET_NAME` | `caseintel-documents` | No |
   | `S3_REGION` | `us-east-1` | No |
   | `CHROMA_PERSIST_DIR` | `/tmp/chroma` | No |
   | `LOG_LEVEL` | `INFO` | No |

8. **Auto Scaling**
   - Min instances: **0** (scale to zero to save money)
   - Max instances: **3**
   - Max concurrency: **100** requests per instance

9. **Health Check**
   - Protocol: **HTTP**
   - Path: `/health`
   - Interval: **10** seconds
   - Timeout: **5** seconds
   - Healthy threshold: **1**
   - Unhealthy threshold: **3**

10. **Security**
    - IAM role: **Create new service role** (first time)
    - Or select existing: `AppRunnerECRAccessRole`

11. **Networking** (Optional - for now, use default)
    - VPC connector: **None** (Railway is public)
    - Later: Create VPC connector for private RDS

12. **Observability** (Optional)
    - AWS X-Ray: **Disabled** (save costs)
    - CloudWatch Logs: **Enabled** (default)

13. **Review and Create**
    - Review all settings
    - Click "Create & deploy"
    - ⏳ Wait 5-10 minutes for deployment

### Step 3: Get Your URL

After deployment completes:

1. **Copy Service URL**
   - Format: `https://abc123xyz.us-east-1.awsapprunner.com`
   - Save this URL!

2. **Test Health Endpoint**
   ```bash
   curl https://your-url.awsapprunner.com/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-15T10:30:00Z",
     "version": "1.0.0"
   }
   ```

3. **Test API with Authentication**
   ```bash
   curl -X POST https://your-url.awsapprunner.com/api/v1/analyze \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key" \
     -d '{
       "document_text": "Test document",
       "case_id": "test-123"
     }'
   ```

---

## Post-Deployment

### Step 4: Update Backend Configuration

```typescript
// backend/caseintel-backend/.env
PYTHON_AGENTS_URL=https://your-url.awsapprunner.com
AGENTS_API_KEY=your_production_api_key
```

### Step 5: Monitor First Week

1. **Check CloudWatch Logs**
   - App Runner → Your Service → Logs
   - Look for errors or warnings

2. **Monitor Costs**
   - AWS Billing Dashboard
   - Should be ~$0.20-0.30/day ($6-9/month)

3. **Check Performance**
   - Response times should be < 30s
   - Cold starts (if min=0) will be 10-15s
   - Warm requests should be < 5s

### Step 6: Set Up Alerts (Optional)

```bash
# Create CloudWatch alarm for errors
aws cloudwatch put-metric-alarm \
  --alarm-name caseintel-agents-errors \
  --alarm-description "Alert on agent errors" \
  --metric-name 4xxStatusResponses \
  --namespace AWS/AppRunner \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

---

## Troubleshooting

### Deployment Failed

**Check:**
1. GitHub connection is active
2. `apprunner.yaml` syntax is correct
3. `requirements.txt` has all dependencies
4. Branch name is correct

**View Logs:**
```bash
# AWS Console
App Runner → Your Service → Deployment logs

# Or CLI
aws apprunner list-operations \
  --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/caseintel-agents
```

### Health Check Failing

**Check:**
1. App is starting correctly
2. Port 8000 is exposed
3. `/health` endpoint exists

**Fix:**
```bash
# View application logs
aws logs tail /aws/apprunner/caseintel-agents/application --follow
```

### Database Connection Error

**Check:**
1. `DATABASE_URL` is correct
2. Railway allows connections from AWS
3. SSL mode is set correctly

**Test Connection:**
```python
# Add to health endpoint temporarily
from src.services.db import check_db_connection

@router.get("/health")
async def health_check():
    db_healthy = check_db_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }
```

### AWS Bedrock Access Denied

**Check:**
1. AWS credentials are correct
2. IAM user/role has Bedrock permissions
3. Region is us-east-1

**Required IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Cost Monitoring

### Expected Costs (First Month)

- **Compute**: 1 vCPU × 730 hours × $0.007 = $5.11
- **Memory**: 2GB × 730 hours × $0.0008 = $1.17
- **Requests**: ~100K × $0.10/million = $0.01
- **Data Transfer**: ~10GB × $0.09/GB = $0.90
- **Total**: ~$7.19/month

### If Costs Are Higher

1. **Reduce to min=0 instances** (scale to zero)
   - Saves ~$3/month
   - Adds 10-15s cold start

2. **Reduce memory to 1GB**
   - Saves ~$0.60/month
   - Monitor for OOM errors

3. **Optimize request batching**
   - Process multiple docs per request
   - Reduces per-request overhead

---

## Next Steps

- [ ] Deploy to App Runner
- [ ] Test with production data
- [ ] Monitor costs for 1 week
- [ ] Integrate with NestJS backend
- [ ] Update frontend to display results
- [ ] Set up custom domain (optional)
- [ ] Configure CI/CD (optional)

---

## Rollback Plan

If something goes wrong:

1. **Pause Deployments**
   ```bash
   aws apprunner pause-service \
     --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/caseintel-agents
   ```

2. **Revert to Previous Version**
   - App Runner → Your Service → Deployments
   - Click on previous successful deployment
   - Click "Redeploy"

3. **Delete Service** (if needed)
   ```bash
   aws apprunner delete-service \
     --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/caseintel-agents
   ```

---

## Success Criteria

✅ Service is running
✅ Health check returns 200
✅ Can analyze a test document
✅ Results are stored in database
✅ Costs are under $10/month
✅ Response times are acceptable

Ready to deploy!
