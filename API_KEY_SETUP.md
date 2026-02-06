# 🔐 API Key Setup Guide

## What is CASEINTEL_API_KEY?

The `CASEINTEL_API_KEY` is a shared secret that authenticates requests between:
- **NestJS Backend** → **Python Agents API**

This ensures only your backend can trigger document analysis on the agents service.

## Current Setup

You already have a key configured in both `.env` files:

```bash
CASEINTEL_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

This key is:
- ✅ Already in `agents/.env`
- ✅ Already in `backend/caseintel-backend/.env`
- ✅ A secure 64-character hex string

## How It Works

### 1. Backend Makes Request

When your NestJS backend calls the agents API:

```typescript
// In backend code
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.CASEINTEL_API_KEY  // ← Key sent here
  },
  body: JSON.stringify({
    document_url: 's3://bucket/document.pdf',
    case_id: 'case-123'
  })
});
```

### 2. Agents API Validates

The Python agents API checks the key:

```python
# In agents/src/api/dependencies.py
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("CASEINTEL_API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### 3. Request Proceeds

If the key matches, the request is processed. If not, you get:

```json
{
  "detail": "Invalid API key"
}
```

## Verify Your Setup

### Check Both .env Files

```bash
# Check agents .env
cd agents
grep CASEINTEL_API_KEY .env

# Check backend .env
cd ../backend/caseintel-backend
grep CASEINTEL_API_KEY .env

# Both should show the SAME key:
# CASEINTEL_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

### Test the Key

```bash
# Test with correct key (should work)
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
  -d '{
    "document_url": "test",
    "case_id": "test"
  }'

# Test with wrong key (should fail)
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{
    "document_url": "test",
    "case_id": "test"
  }'
# Expected: {"detail": "Invalid API key"}
```

## Generate a New Key (Optional)

If you want to generate a new API key:

### Option 1: Using Python

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Option 2: Using OpenSSL

```bash
openssl rand -hex 32
```

### Option 3: Using Node.js

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Then update **both** `.env` files with the new key.

## Security Best Practices

### ✅ DO:

1. **Keep the key secret** - Never commit to git
2. **Use different keys** for development and production
3. **Rotate keys periodically** (every 90 days)
4. **Use environment variables** - Never hardcode in source code
5. **Use HTTPS in production** - Encrypt the key in transit

### ❌ DON'T:

1. **Don't share the key** publicly
2. **Don't use simple/guessable keys** like "test123"
3. **Don't commit .env files** to version control
4. **Don't reuse keys** across different environments
5. **Don't log the key** in application logs

## Production Setup

For production deployment, use different keys:

### Development (.env.development)
```bash
CASEINTEL_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

### Production (.env.production)
```bash
CASEINTEL_API_KEY=<generate-new-key-for-production>
```

### AWS Deployment

When deploying to AWS, store the key in:

1. **AWS Secrets Manager** (recommended)
   ```bash
   aws secretsmanager create-secret \
     --name caseintel/api-key \
     --secret-string "your-production-key"
   ```

2. **AWS Systems Manager Parameter Store**
   ```bash
   aws ssm put-parameter \
     --name /caseintel/api-key \
     --value "your-production-key" \
     --type SecureString
   ```

3. **Environment Variables in ECS/Lambda**
   - Set in task definition (ECS)
   - Set in function configuration (Lambda)

## Troubleshooting

### Issue: "Invalid API key" error

**Cause**: Key mismatch between backend and agents

**Fix**:
```bash
# 1. Check both files have the same key
diff <(grep CASEINTEL_API_KEY agents/.env) \
     <(grep CASEINTEL_API_KEY backend/caseintel-backend/.env)

# 2. If different, copy from one to the other
# 3. Restart both services
```

### Issue: Key not being read

**Cause**: Environment variable not loaded

**Fix**:
```bash
# For agents (Python)
cd agents
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('CASEINTEL_API_KEY'))"

# For backend (Node.js)
cd backend/caseintel-backend
node -e "require('dotenv').config(); console.log(process.env.CASEINTEL_API_KEY)"
```

### Issue: Header not being sent

**Cause**: Backend not including the header

**Fix**: Check your backend code includes the header:
```typescript
headers: {
  'X-API-Key': process.env.CASEINTEL_API_KEY
}
```

## Testing the Full Flow

### 1. Start Agents API
```bash
cd agents
./venv/bin/uvicorn src.api.main:app --reload --port 8000
```

### 2. Test with curl
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6" \
  -d '{
    "document_url": "s3://caseintel-documents/test.pdf",
    "case_id": "test-case-123"
  }'
```

### 3. Expected Response
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Document analysis started"
}
```

## Key Rotation Process

When rotating keys:

1. **Generate new key**
   ```bash
   NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   echo "New key: $NEW_KEY"
   ```

2. **Update agents .env**
   ```bash
   cd agents
   # Update CASEINTEL_API_KEY in .env
   ```

3. **Update backend .env**
   ```bash
   cd backend/caseintel-backend
   # Update CASEINTEL_API_KEY in .env
   ```

4. **Restart both services**
   ```bash
   # Restart agents API
   # Restart backend API
   ```

5. **Test the connection**
   ```bash
   # Run test curl command
   ```

## Summary

✅ **Your current setup is correct!**

Both `.env` files have the same key:
```
CASEINTEL_API_KEY=4516040c95e8d79ef0aa5febba95e1e8b369ca9faa238feaf9e1ffadf0582aa6
```

This key:
- Is secure (64 characters, randomly generated)
- Is already configured in both services
- Will work for local development

**Next steps:**
1. Test the API with the key (see "Testing the Full Flow" above)
2. Generate a new key for production when deploying to AWS
3. Store production key in AWS Secrets Manager

---

**Need help?** Run the test script:
```bash
cd agents
./test_api.sh
```
