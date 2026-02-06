# 📚 CaseIntel Documentation Index

Welcome to CaseIntel AI Agents! This index will help you find the right documentation for your needs.

## 🚀 Getting Started

### New Users - Start Here!

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡
   - 5-minute setup guide
   - Step-by-step instructions
   - First document analysis
   - Common commands
   - **Start here if you want to get running fast!**

2. **[READY_TO_USE.md](READY_TO_USE.md)** 🎯
   - Quick reference guide
   - 3-step setup
   - API endpoint examples
   - Troubleshooting tips
   - **Use this for quick lookups!**

## 📖 Core Documentation

### Project Overview

3. **[README.md](README.md)** 📋
   - Complete project documentation
   - Architecture overview
   - Feature list
   - Installation guide
   - **Read this for comprehensive understanding!**

4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 📊
   - High-level project summary
   - Technology stack
   - Cost analysis
   - Performance metrics
   - **Great for stakeholders and team members!**

## ⚙️ Configuration Guides

### AWS Bedrock Setup

5. **[BEDROCK_SETUP.md](BEDROCK_SETUP.md)** ☁️
   - AWS Bedrock configuration
   - Model access setup
   - Credential management
   - Testing instructions
   - **Essential for AWS setup!**

6. **[BEDROCK_MIGRATION_COMPLETE.md](BEDROCK_MIGRATION_COMPLETE.md)** 🔄
   - Migration from Anthropic API
   - Changes made to codebase
   - Before/after comparison
   - **Historical reference for the migration!**

### Model Configuration

7. **[DEVELOPMENT_MODELS.md](DEVELOPMENT_MODELS.md)** 💰
   - Development vs production models
   - Cost comparison
   - Model selection guide
   - Switching between environments
   - **Read this to understand model costs!**

8. **[CLAUDE_45_UPGRADE.md](CLAUDE_45_UPGRADE.md)** 🆙
   - Claude 4.5 model information
   - Upgrade instructions
   - Model IDs and specifications
   - **Reference for production models!**

## ✅ Setup & Verification

9. **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** ✔️
   - Complete setup summary
   - Configuration checklist
   - Next steps
   - Troubleshooting
   - **Verify your setup is complete!**

## 📐 Original Specification

10. **[CASEINTEL_AGENTS.md](CASEINTEL_AGENTS.md)** 📝
    - Original project specification
    - Agent descriptions
    - Workflow design
    - Requirements
    - **Reference for original design decisions!**

## 🗂️ Documentation by Use Case

### I want to...

#### Get Started Quickly
→ **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup

#### Understand the Project
→ **[README.md](README.md)** - Full documentation
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level overview

#### Configure AWS Bedrock
→ **[BEDROCK_SETUP.md](BEDROCK_SETUP.md)** - AWS setup guide
→ **[DEVELOPMENT_MODELS.md](DEVELOPMENT_MODELS.md)** - Model selection

#### Understand Costs
→ **[DEVELOPMENT_MODELS.md](DEVELOPMENT_MODELS.md)** - Cost analysis
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Cost breakdown

#### Troubleshoot Issues
→ **[READY_TO_USE.md](READY_TO_USE.md)** - Quick troubleshooting
→ **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Setup verification

#### Switch to Production
→ **[DEVELOPMENT_MODELS.md](DEVELOPMENT_MODELS.md)** - Switching guide
→ **[CLAUDE_45_UPGRADE.md](CLAUDE_45_UPGRADE.md)** - Production models

#### Understand the Architecture
→ **[README.md](README.md)** - Architecture section
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Architecture diagram
→ **[CASEINTEL_AGENTS.md](CASEINTEL_AGENTS.md)** - Original design

## 📁 Code Documentation

### Key Files to Understand

#### Agents
- `src/agents/base.py` - Base agent with Bedrock integration
- `src/agents/classifier.py` - Document classification
- `src/agents/privilege_checker.py` - Privilege detection
- `src/agents/hot_doc_detector.py` - Hot document detection
- `src/agents/content_analyzer.py` - Content analysis
- `src/agents/metadata_extractor.py` - Metadata extraction
- `src/agents/cross_reference.py` - Cross-referencing

#### RAG System
- `src/rag/embeddings.py` - Bedrock embeddings (Titan)
- `src/rag/chunking.py` - Document chunking
- `src/rag/retrieval.py` - Semantic search

#### Workflows
- `src/workflows/discovery_pipeline.py` - LangGraph orchestration
- `src/workflows/state.py` - Workflow state management

#### API
- `src/api/main.py` - FastAPI application
- `src/api/routes/analyze.py` - Analysis endpoint
- `src/api/routes/search.py` - Search endpoint

#### Database
- `src/models/database.py` - SQLAlchemy models
- `src/models/schemas.py` - Pydantic schemas

## 🛠️ Utility Scripts

### Verification & Testing

- `scripts/verify_setup.py` - Complete setup verification
- `scripts/test_bedrock.py` - Test Bedrock connection
- `scripts/seed_vectors.py` - Seed vector database

### Running Scripts

```bash
# Verify setup
python scripts/verify_setup.py

# Test Bedrock
python scripts/test_bedrock.py

# Seed vectors
python scripts/seed_vectors.py
```

## 🎯 Quick Reference

### Essential Commands

```bash
# Start services
docker-compose up -d
uvicorn src.api.main:app --reload

# Verify setup
python scripts/verify_setup.py

# Test Bedrock
python scripts/test_bedrock.py

# Stop services
docker-compose down
```

### Essential URLs

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Essential Files

- Configuration: `.env`
- Dependencies: `requirements.txt`
- Docker: `docker-compose.yml`

## 📊 Documentation Statistics

- **Total Documents**: 10 markdown files
- **Total Lines**: ~1,500 lines of documentation
- **Coverage**: Complete project documentation
- **Last Updated**: February 5, 2026

## 🔄 Documentation Updates

### Recent Changes

- ✅ Added AWS Bedrock integration docs
- ✅ Added development model configuration
- ✅ Added cost analysis
- ✅ Added troubleshooting guides
- ✅ Added quick start guide
- ✅ Added setup verification

### Keeping Documentation Updated

When making changes to the project:

1. Update relevant documentation files
2. Update this index if adding new docs
3. Update version numbers
4. Update last modified dates

## 💡 Tips for Using Documentation

### For Developers

1. Start with **QUICKSTART.md** to get running
2. Read **README.md** for architecture understanding
3. Reference **DEVELOPMENT_MODELS.md** for costs
4. Use **READY_TO_USE.md** for quick lookups

### For DevOps/Deployment

1. Read **BEDROCK_SETUP.md** for AWS configuration
2. Review **PROJECT_SUMMARY.md** for architecture
3. Check **SETUP_COMPLETE.md** for deployment checklist
4. Use **DEVELOPMENT_MODELS.md** for environment config

### For Project Managers

1. Read **PROJECT_SUMMARY.md** for overview
2. Review **DEVELOPMENT_MODELS.md** for costs
3. Check **README.md** for features
4. Reference **CASEINTEL_AGENTS.md** for requirements

### For End Users

1. Start with **QUICKSTART.md**
2. Use **READY_TO_USE.md** for API examples
3. Reference **README.md** for features
4. Check **SETUP_COMPLETE.md** for troubleshooting

## 🆘 Getting Help

### Troubleshooting Steps

1. Run `python scripts/verify_setup.py`
2. Check **READY_TO_USE.md** troubleshooting section
3. Review **SETUP_COMPLETE.md** for common issues
4. Check AWS Bedrock console for model access
5. Review logs: `docker-compose logs -f`

### Common Issues

| Issue | Documentation |
|-------|---------------|
| Setup problems | SETUP_COMPLETE.md |
| AWS credentials | BEDROCK_SETUP.md |
| Model costs | DEVELOPMENT_MODELS.md |
| API usage | READY_TO_USE.md |
| Architecture questions | PROJECT_SUMMARY.md |

## 📝 Contributing to Documentation

When adding new documentation:

1. Follow the existing format and style
2. Add entry to this index
3. Update related documents
4. Include code examples
5. Add troubleshooting tips

## 🎓 Learning Path

### Beginner Path

1. **QUICKSTART.md** - Get started
2. **READY_TO_USE.md** - Learn API basics
3. **README.md** - Understand features
4. **DEVELOPMENT_MODELS.md** - Learn about costs

### Advanced Path

1. **PROJECT_SUMMARY.md** - Architecture deep dive
2. **CASEINTEL_AGENTS.md** - Design decisions
3. **BEDROCK_SETUP.md** - AWS configuration
4. Code files - Implementation details

## 📞 Support Resources

- **Documentation**: This index and linked files
- **Scripts**: `scripts/verify_setup.py`, `scripts/test_bedrock.py`
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/torrancejr/caseintel-agents

---

**Last Updated**: February 5, 2026

**Documentation Version**: 1.0.0

**Project Status**: ✅ Production Ready

---

## Quick Navigation

- [⚡ Quick Start](QUICKSTART.md)
- [🎯 Ready to Use](READY_TO_USE.md)
- [📋 README](README.md)
- [📊 Project Summary](PROJECT_SUMMARY.md)
- [☁️ Bedrock Setup](BEDROCK_SETUP.md)
- [💰 Development Models](DEVELOPMENT_MODELS.md)
- [✔️ Setup Complete](SETUP_COMPLETE.md)

**Happy coding! 🚀**
