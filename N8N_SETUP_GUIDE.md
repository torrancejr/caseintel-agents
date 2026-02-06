# 🔧 n8n Setup Guide for CaseIntel

## Quick Start: Get n8n Running in 10 Minutes

### Option 1: Docker (Recommended for Demo)

```bash
# Pull n8n image
docker pull n8nio/n8n

# Run n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Access at: http://localhost:5678

### Option 2: npm (For Development)

```bash
# Install globally
npm install n8n -g

# Run n8n
n8n start
```

Access at: http://localhost:5678

### Option 3: Docker Compose (For Production)

Create `docker-compose.n8n.yml`:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password
      - N8N_HOST=n8n.caseintel.io
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.caseintel.io/
      - GENERIC_TIMEZONE=America/New_York
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - caseintel

  postgres:
    image: postgres:16
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - caseintel

volumes:
  n8n_data:
  postgres_data:

networks:
  caseintel:
    external: true
```

Run:
```bash
docker-compose -f docker-compose.n8n.yml up -d
```

---

## Creating Your First Workflow

### Workflow 1: Document Intake via Email

1. **Open n8n** → http://localhost:5678
2. **Create New Workflow** → Click "+" button
3. **Add Nodes:**

#### Node 1: Email Trigger
- Search for "Email Trigger (IMAP)"
- Configure:
  - Host: `imap.gmail.com`
  - Port: `993`
  - User: `intake@caseintel.io`
  - Password: `your-app-password`
  - Folder: `INBOX`

#### Node 2: Extract Attachments
- Search for "Extract from File"
- Connect to Email Trigger
- Configure:
  - Binary Property: `attachment_0`
  - Extract: `All`

#### Node 3: HTTP Request (Upload to S3)
- Search for "HTTP Request"
- Configure:
  - Method: `POST`
  - URL: `https://api.caseintel.io/upload`
  - Authentication: `Header Auth`
  - Header Name: `X-API-Key`
  - Header Value: `your-api-key`
  - Body: `{{ $json.data }}`

#### Node 4: HTTP Request (Create Document)
- Search for "HTTP Request"
- Configure:
  - Method: `POST`
  - URL: `https://api.caseintel.io/documents`
  - Body:
    ```json
    {
      "caseId": "{{ $json.caseId }}",
      "filename": "{{ $json.filename }}",
      "s3Key": "{{ $json.s3Key }}"
    }
    ```

#### Node 5: Wait (for OCR)
- Search for "Wait"
- Configure:
  - Wait Time: `30 seconds`

#### Node 6: HTTP Request (Trigger Analysis)
- Search for "HTTP Request"
- Configure:
  - Method: `POST`
  - URL: `http://localhost:8001/api/v1/analyze`
  - Body:
    ```json
    {
      "case_id": "{{ $json.caseId }}",
      "document_id": "{{ $json.documentId }}",
      "document_text": "{{ $json.text }}"
    }
    ```

#### Node 7: IF (Check Hot Doc)
- Search for "IF"
- Configure:
  - Condition: `{{ $json.is_hot_doc }} === true`

#### Node 8a: Slack (Hot Doc Alert)
- Search for "Slack"
- Configure:
  - Channel: `#hot-docs`
  - Message: `🔥 Hot Doc Found: {{ $json.document_id }}`

#### Node 8b: Email (Regular Digest)
- Search for "Send Email"
- Configure:
  - To: `attorney@lawfirm.com`
  - Subject: `Document Analyzed`
  - Body: `Document {{ $json.document_id }} has been analyzed.`

4. **Save Workflow** → Name it "Document Intake"
5. **Activate** → Toggle switch to ON

---

## Custom Nodes for CaseIntel

### Create Custom Node: CaseIntel Agents

Create `nodes/CaseIntelAgents/CaseIntelAgents.node.ts`:

```typescript
import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
} from 'n8n-workflow';

export class CaseIntelAgents implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'CaseIntel Agents',
    name: 'caseIntelAgents',
    icon: 'file:caseintel.svg',
    group: ['transform'],
    version: 1,
    description: 'Analyze documents with CaseIntel AI Agents',
    defaults: {
      name: 'CaseIntel Agents',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'caseIntelApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          {
            name: 'Analyze Document',
            value: 'analyze',
          },
          {
            name: 'Get Status',
            value: 'status',
          },
          {
            name: 'Search Documents',
            value: 'search',
          },
        ],
        default: 'analyze',
      },
      {
        displayName: 'Case ID',
        name: 'caseId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            operation: ['analyze'],
          },
        },
      },
      {
        displayName: 'Document ID',
        name: 'documentId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: {
          show: {
            operation: ['analyze', 'status'],
          },
        },
      },
      {
        displayName: 'Document Text',
        name: 'documentText',
        type: 'string',
        typeOptions: {
          rows: 10,
        },
        default: '',
        required: true,
        displayOptions: {
          show: {
            operation: ['analyze'],
          },
        },
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];
    const operation = this.getNodeParameter('operation', 0) as string;
    const credentials = await this.getCredentials('caseIntelApi');

    for (let i = 0; i < items.length; i++) {
      if (operation === 'analyze') {
        const caseId = this.getNodeParameter('caseId', i) as string;
        const documentId = this.getNodeParameter('documentId', i) as string;
        const documentText = this.getNodeParameter('documentText', i) as string;

        const response = await this.helpers.request({
          method: 'POST',
          url: `${credentials.apiUrl}/api/v1/analyze`,
          headers: {
            'X-API-Key': credentials.apiKey,
            'Content-Type': 'application/json',
          },
          body: {
            case_id: caseId,
            document_id: documentId,
            document_text: documentText,
          },
          json: true,
        });

        returnData.push({ json: response });
      }
    }

    return [returnData];
  }
}
```

---

## Workflow Templates for CaseIntel

### Template 1: Batch Processing

```json
{
  "name": "Batch Document Processing",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "batch-upload",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Split In Batches",
      "type": "n8n-nodes-base.splitInBatches",
      "position": [450, 300],
      "parameters": {
        "batchSize": 10
      }
    },
    {
      "name": "CaseIntel Agents",
      "type": "caseIntelAgents",
      "position": [650, 300],
      "parameters": {
        "operation": "analyze",
        "caseId": "={{ $json.caseId }}",
        "documentId": "={{ $json.documentId }}",
        "documentText": "={{ $json.text }}"
      }
    },
    {
      "name": "Aggregate",
      "type": "n8n-nodes-base.aggregate",
      "position": [850, 300],
      "parameters": {
        "aggregate": "aggregateAllItemData"
      }
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "position": [1050, 300],
      "parameters": {
        "toEmail": "attorney@lawfirm.com",
        "subject": "Batch Processing Complete",
        "text": "Processed {{ $json.length }} documents"
      }
    }
  ]
}
```

### Template 2: Hot Doc Alert

```json
{
  "name": "Hot Document Alert System",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "hot-doc-check"
      }
    },
    {
      "name": "CaseIntel Agents",
      "type": "caseIntelAgents",
      "position": [450, 300],
      "parameters": {
        "operation": "analyze"
      }
    },
    {
      "name": "IF Hot Doc",
      "type": "n8n-nodes-base.if",
      "position": [650, 300],
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.is_hot_doc }}",
              "value2": true
            }
          ]
        }
      }
    },
    {
      "name": "Slack Alert",
      "type": "n8n-nodes-base.slack",
      "position": [850, 200],
      "parameters": {
        "channel": "#hot-docs",
        "text": "🔥 Hot Doc: {{ $json.document_id }}\nSeverity: {{ $json.hot_doc_severity }}"
      }
    },
    {
      "name": "SMS Alert",
      "type": "n8n-nodes-base.twilio",
      "position": [850, 300],
      "parameters": {
        "to": "+1234567890",
        "message": "🔥 Critical hot doc found!"
      }
    },
    {
      "name": "Email Alert",
      "type": "n8n-nodes-base.emailSend",
      "position": [850, 400],
      "parameters": {
        "toEmail": "attorney@lawfirm.com",
        "subject": "🔥 Hot Document Alert",
        "text": "A critical document has been identified."
      }
    }
  ]
}
```

---

## Integration with CaseIntel APIs

### Backend API Endpoints

```javascript
// In your NestJS backend, add n8n webhook endpoints

@Post('webhooks/n8n/document-processed')
async handleDocumentProcessed(@Body() data: any) {
  // Trigger n8n workflow
  await this.httpService.post(
    'http://localhost:5678/webhook/document-processed',
    data
  ).toPromise();
}
```

### Agents API Endpoints

```python
# In your FastAPI agents, add n8n integration

@app.post("/webhooks/n8n/analysis-complete")
async def notify_n8n(result: AnalysisResult):
    """Notify n8n when analysis is complete"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:5678/webhook/analysis-complete",
            json=result.dict()
        )
```

---

## Monitoring & Debugging

### View Workflow Executions

1. Go to **Executions** tab in n8n
2. See all workflow runs
3. Click to view details
4. Debug failed executions

### Enable Logging

```bash
# Set environment variable
export N8N_LOG_LEVEL=debug

# Restart n8n
n8n start
```

### Webhook Testing

```bash
# Test webhook with curl
curl -X POST http://localhost:5678/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## Production Deployment

### Deploy to AWS

1. **EC2 Instance**
   - t3.medium (2 vCPU, 4GB RAM)
   - Ubuntu 22.04
   - Install Docker

2. **Setup n8n**
   ```bash
   docker-compose -f docker-compose.n8n.yml up -d
   ```

3. **Configure Domain**
   - Point `n8n.caseintel.io` to EC2 IP
   - Setup SSL with Let's Encrypt

4. **Secure Access**
   - Enable basic auth
   - Use strong passwords
   - Restrict IP access

### Environment Variables

```bash
# Production .env for n8n
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=strong-password-here
N8N_HOST=n8n.caseintel.io
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.caseintel.io/
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=n8n_password
```

---

## Cost Estimate

### Self-Hosted (Recommended)

- **EC2 t3.medium**: $30/month
- **Storage (50GB)**: $5/month
- **Data Transfer**: $10/month
- **Total**: ~$45/month

### n8n Cloud (Alternative)

- **Starter**: $20/month (5K executions)
- **Pro**: $50/month (25K executions)
- **Enterprise**: Custom pricing

**Recommendation**: Self-host for full control and lower costs

---

## Next Steps

1. ✅ Install n8n locally
2. ✅ Create first workflow (document intake)
3. ✅ Test with sample document
4. ✅ Add Slack/email notifications
5. ✅ Create batch processing workflow
6. ✅ Deploy to production
7. ✅ Monitor and optimize

---

**Questions?** Check the [n8n documentation](https://docs.n8n.io) or contact ryan@caseintel.io
