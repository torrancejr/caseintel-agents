# 🚀 Ready to Deploy to AWS App Runner

## ✅ What's Complete

1. **Clean Branch Created**: `feature/agents-deploy`
   - No sensitive credentials in git history
   - All deployment files included
   - Successfully pushed to GitHub

2. **Deployment Files Ready**:
   - ✅ `apprunner.yaml` - App Runner configuration
   - ✅ `.apprunnerignore` - Files to exclude from deployment
   - ✅ `.env.production.example` - Template for production env vars
   - ✅ `AWS_DEPLOYMENT.md` - Complete deployment guide
   - ✅ `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
   - ✅ `INTEGRATION_PLAN.md` - Post-deployment integration plan

3. **Local Testing Verified**:
   - ✅ API running on localhost:8000
   - ✅ Database connection working
   - ✅ AWS Bedrock access confirmed (125 models)
   - ✅ Document analysis working
   - ✅ Cross-reference functionality tested

---

## 🎯 Next Steps: Deploy to AWS

### Step 1: Gather Your Environment Variables

You'll need these from your `agents/.env` file:

```bash
DATABASE_URL=postgresql://caseintel:...@...railway.app:5432/railway
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
CASEINTEL_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
S3_BUCKET_NAME=caseintel-documents
S3_REGION=us-east-1
```

### Step 2: Go to AWS Console

1. Open: https://console.aws.amazon.com/apprunner
2. Region: **us-east-1** (top right corner)
3. Click **"Create service"**

### Step 3: Configure Source

1. **Repository type**: Source code repository
2. **Provider**: GitHub
3. Click **"Add new"** to connect GitHub (first time only)
4. **Repository**: Select `torrancejr/caseintel-agents`
5. **Branch**: `feature/agents-deploy`
6. **Deployment trigger**: Automatic
7. Click **"Next"**

### Step 4: Configure Build

1. **Configuration file**: Use a configuration file
2. **Configuration file path**: `agents/apprunner.yaml`
3. Click **"Next"**

### Step 5: Configure Service

1. **Service name**: `caseintel-agents`
2. **Virtual CPU**: 1 vCPU
3. **Memory**: 2 GB
4. **Port**: 8000

### Step 6: Add Environment Variables

Click "Add environment variable" for each:

| Name | Value | Secret? |
|------|-------|---------|
| `DATABASE_URL` | Your Railway PostgreSQL URL | ✅ Yes |
| `AWS_REGION` | `us-east-1` | No |
| `AWS_ACCESS_KEY_ID` | Your AWS key | ✅ Yes |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret | ✅ Yes |
| `CASEINTEL_API_KEY` | Your API key | ✅ Yes |
| `S3_BUCKET_NAME` | `caseintel-documents` | No |
| `S3_REGION` | `us-east-1` | No |
| `CHROMA_PERSIST_DIR` | `/tmp/chroma` | No |
| `LOG_LEVEL` | `INFO` | No |

### Step 7: Configure Auto Scaling

1. **Min instances**: 0 (scale to zero to save money)
2. **Max instances**: 3
3. **Max concurrency**: 100

### Step 8: Configure Health Check

1. **Protocol**: HTTP
2. **Path**: `/health`
3. **Interval**: 10 seconds
4. **Timeout**: 5 seconds
5. **Healthy threshold**: 1
6. **Unhealthy threshold**: 3

### Step 9: Review and Deploy

1. Review all settings
2. Click **"Create & deploy"**
3. ⏳ Wait 5-10 minutes for deployment

---

## 📊 Expected Costs

- **Compute**: $5.11/month (1 vCPU × 730 hours)
- **Memory**: $1.17/month (2GB × 730 hours)
- **Requests**: $0.01/month (~100K requests)
- **Total**: ~$6.29/month

With min instances = 0, you'll save ~$3/month but have 10-15s cold starts.

---

## ✅ After Deployment

### 1. Get Your Service URL

After deployment completes, you'll get a URL like:
```
https://abc123xyz.us-east-1.awsapprunner.com
```

### 2. Test the Deployment

```bash
# Test health endpoint
curl https://your-url.awsapprunner.com/health

# Test document analysis
curl -X POST https://your-url.awsapprunner.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
  -d '{
    "document_text": "Test legal document for deployment verification",
    "case_id": "00000000-0000-0000-0000-000000000003"
  }'
```

### 3. Update Backend Configuration

Once deployed, update your NestJS backend:

```typescript
// backend/caseintel-backend/.env
PYTHON_AGENTS_URL=https://your-url.awsapprunner.com
AGENTS_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

---

## 🔍 Monitoring

### View Logs
- AWS Console: App Runner → caseintel-agents → Logs
- Watch for startup messages and any errors

### Check Metrics
- Request count
- Response times (should be < 30s)
- Error rate (should be < 1%)
- CPU/Memory usage

---

## 🆘 Troubleshooting

### If Deployment Fails
1. Check deployment logs in AWS Console
2. Verify all environment variables are set
3. Verify GitHub connection is active
4. Check `apprunner.yaml` syntax

### If Health Check Fails
1. Check application logs
2. Verify port 8000 is correct
3. Verify `/health` endpoint exists

### If Database Connection Fails
1. Verify `DATABASE_URL` is correct
2. Check Railway allows connections from AWS
3. Verify SSL mode is set correctly

---

## 📚 Reference Documents

- `AWS_DEPLOYMENT.md` - Complete deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Detailed step-by-step checklist
- `INTEGRATION_PLAN.md` - Post-deployment integration plan

---

## 🎉 Success Criteria

- ✅ Service is running
- ✅ Health check returns 200
- ✅ Can analyze a test document
- ✅ Results stored in database
- ✅ Costs under $10/month
- ✅ Response times acceptable

---

**Ready to deploy!** Follow the steps above and let me know when you have your service URL.
