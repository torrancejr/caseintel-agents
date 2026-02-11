#!/bin/bash

# Load environment variables from .env
source .env

# Create deployment JSON
cat > deployment.json <<EOF
{
  "containers": {
    "caseintel-agents": {
      "image": ":caseintel-agents-1.latest.1",
      "ports": {
        "8000": "HTTP"
      },
      "environment": {
        "DATABASE_URL": "${DATABASE_URL}",
        "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
        "AWS_REGION": "${AWS_REGION}",
        "CASEINTEL_API_KEY": "${CASEINTEL_API_KEY}",
        "S3_BUCKET": "${S3_BUCKET}",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "CHROMA_PERSIST_DIR": "/tmp/chroma_db",
        "MODEL_CLASSIFIER": "${MODEL_CLASSIFIER}",
        "MODEL_METADATA": "${MODEL_METADATA}",
        "MODEL_PRIVILEGE": "${MODEL_PRIVILEGE}",
        "MODEL_HOTDOC": "${MODEL_HOTDOC}",
        "MODEL_CONTENT": "${MODEL_CONTENT}",
        "MODEL_CROSSREF": "${MODEL_CROSSREF}",
        "EMBEDDING_MODEL": "${EMBEDDING_MODEL}"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "caseintel-agents",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/health",
      "intervalSeconds": 30,
      "timeoutSeconds": 10,
      "healthyThreshold": 2,
      "unhealthyThreshold": 2
    }
  }
}
EOF

echo "Deploying to Lightsail with environment variables..."

aws lightsail create-container-service-deployment \
  --service-name caseintel-agents-1 \
  --region us-east-1 \
  --cli-input-json file://deployment.json

echo ""
echo "Deployment initiated! Check status with:"
echo "aws lightsail get-container-services --service-name caseintel-agents-1 --region us-east-1"

# Clean up
rm deployment.json
