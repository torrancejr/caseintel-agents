# AWS Lightsail Container Deployment Guide

## Prerequisites
- AWS CLI installed and configured
- Docker installed locally
- Railway PostgreSQL database URL

## Step 1: Build Docker Image Locally

```bash
cd agents
docker build -t caseintel-agents:latest .
```

## Step 2: Push Image to Lightsail

```bash
aws lightsail push-container-image \
  --service-name caseintel-agents \
  --label latest \
  --image caseintel-agents:latest \
  --region us-east-1
```

**Note**: If the service doesn't exist yet, Lightsail will guide you to create it.

## Step 3: Create Container Service (First Time Only)

Go to AWS Lightsail Console:
1. Navigate to "Containers"
2. Click "Create container service"
3. Choose your power level (Nano = $7/month, Micro = $10/month)
4. Service name: `caseintel-agents`
5. Click "Create container service"

## Step 4: Configure Deployment

After pushing the image, create a deployment configuration:

```json
{
  "containers": {
    "caseintel-agents": {
      "image": ":caseintel-agents.latest.1",
      "ports": {
        "8000": "HTTP"
      },
      "environment": {
        "DATABASE_URL": "your-railway-postgres-url",
        "AWS_ACCESS_KEY_ID": "your-aws-key",
        "AWS_SECRET_ACCESS_KEY": "your-aws-secret",
        "AWS_REGION": "us-east-1",
        "CASEINTEL_API_KEY": "your-api-key",
        "S3_BUCKET": "caseintel-documents",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "CHROMA_PERSIST_DIR": "/tmp/chroma_db",
        "MODEL_CLASSIFIER": "anthropic.claude-3-haiku-20240307-v1:0",
        "MODEL_METADATA": "anthropic.claude-3-haiku-20240307-v1:0",
        "MODEL_PRIVILEGE": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "MODEL_HOTDOC": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "MODEL_CONTENT": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "MODEL_CROSSREF": "anthropic.claude-3-haiku-20240307-v1:0",
        "EMBEDDING_MODEL": "amazon.titan-embed-text-v2:0"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "caseintel-agents",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/health",
      "intervalSeconds": 30
    }
  }
}
```

## Step 5: Deploy via Console

1. Go to your Lightsail container service
2. Click "Create your first deployment"
3. Select the image you pushed
4. Add environment variables (from the JSON above)
5. Set public endpoint to port 8000
6. Set health check path to `/health`
7. Click "Save and deploy"

## Step 6: Get Your Public URL

After deployment completes (5-10 minutes):
- Your service will be available at: `https://caseintel-agents.xxxxx.us-east-1.cs.amazonlightsail.com`
- Test it: `curl https://your-url/health`

## Pricing

- **Nano**: $7/month (512 MB RAM, 0.25 vCPU)
- **Micro**: $10/month (1 GB RAM, 0.25 vCPU)
- **Small**: $20/month (2 GB RAM, 0.5 vCPU)

Start with Nano and scale up if needed.

## Updating Your Deployment

When you make code changes:

```bash
# 1. Build new image
docker build -t caseintel-agents:latest .

# 2. Push to Lightsail
aws lightsail push-container-image \
  --service-name caseintel-agents \
  --label latest \
  --image caseintel-agents:latest \
  --region us-east-1

# 3. Lightsail will auto-deploy the new version
```

## Troubleshooting

### View Logs
```bash
aws lightsail get-container-log \
  --service-name caseintel-agents \
  --container-name caseintel-agents \
  --region us-east-1
```

### Check Service Status
```bash
aws lightsail get-container-services \
  --service-name caseintel-agents \
  --region us-east-1
```
