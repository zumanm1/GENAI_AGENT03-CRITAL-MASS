# Network Automation AI Agent - Product Requirements Document (PRD)

## Project Overview
**Project Name:** Network Automation AI Agent with Agentic RAG  
**Version:** 1.0  
**Date:** 2024  
**Status:** In Development  

## Executive Summary
Develop an AI-powered network automation platform that enables users to interact with network devices through natural language, perform network audits, and execute basic configuration tasks using Ollama LLM, RAG capabilities, and network automation tools.

## Core Objectives
1. Enable natural language interaction with network infrastructure
2. Provide intelligent network audit and troubleshooting capabilities
3. Automate basic network configuration tasks
4. Implement document ingestion for network configuration analysis
5. Create a conversational AI interface for network operations

## Technology Stack
- **LLM:** Ollama (Llama 3.1 1B)
- **RAG Framework:** LangChain + CrewAI
- **Vector Database:** ChromaDB
- **Web Framework:** Flask
- **Network Automation:** Netmiko, Nornir, NetPalm, PyATS/Genie
- **Language:** Python 3.9+
- **Database:** SQLite (for metadata), ChromaDB (for vectors)

## Feature Requirements

### 1. Document Ingestion System
- **Priority:** High
- **Description:** Ingest PDF, Excel, and text files containing device configurations
- **Acceptance Criteria:**
  - Support PDF, XLSX, TXT file formats
  - Extract and parse network configuration data
  - Store in vector database for RAG retrieval
  - Maintain metadata for document tracking

### 2. Network Device Discovery
- **Priority:** High
- **Description:** Discover network devices in IP range 172.16.39.107-120
- **Acceptance Criteria:**
  - Scan IP range for active devices
  - Identify device types and capabilities
  - Store device inventory in database
  - Support SSH connectivity testing

### 3. Network Audit Tools
- **Priority:** High
- **Description:** Perform network validation using Netmiko
- **Acceptance Criteria:**
  - OSPF neighbor validation
  - BGP peer status checking
  - Interface status monitoring
  - Connectivity testing (ping)
  - Generate audit reports

### 4. Conversational AI Interface
- **Priority:** High
- **Description:** Natural language interface for network operations
- **Acceptance Criteria:**
  - Chat-based web interface
  - Context-aware responses
  - Support for network queries
  - Command suggestion capabilities

### 5. Configuration Management
- **Priority:** Medium
- **Description:** Basic network configuration capabilities
- **Acceptance Criteria:**
  - Interface IP configuration
  - Interface shutdown/no shutdown
  - Basic routing configuration
  - Configuration backup and restore

### 6. Agent Framework
- **Priority:** Medium
- **Description:** Specialized AI agents for different network roles
- **Acceptance Criteria:**
  - Network Engineer Agent
  - Troubleshooting Agent
  - Configuration Agent
  - Audit Agent

## Task Breakdown & Dependencies

### Phase 1: Foundation (Weeks 1-2)
| Task ID | Task Description | Priority | Dependencies | Assignee | Status |
|---------|------------------|----------|--------------|----------|--------|
| T001 | Project structure setup | High | None | Dev | ✅ Complete |
| T002 | Environment configuration | High | T001 | Dev | ✅ Complete |
| T003 | Ollama integration | High | T002 | Dev | ⏳ Pending |
| T004 | ChromaDB setup | High | T002 | Dev | ⏳ Pending |
| T005 | Basic Flask app | High | T002 | Dev | ✅ Complete |

### Phase 2: Core Features (Weeks 3-4)
| Task ID | Task Description | Priority | Dependencies | Assignee | Status |
|---------|------------------|----------|--------------|----------|--------|
| T006 | Document ingestion system | High | T004 | Dev | ⏳ Pending |
| T007 | Network device discovery | High | T003 | Dev | ⏳ Pending |
| T008 | Netmiko integration | High | T007 | Dev | ⏳ Pending |
| T009 | Basic network audit tools | High | T008 | Dev | ⏳ Pending |
| T010 | RAG implementation | High | T006, T004 | Dev | ⏳ Pending |

### Phase 3: AI Integration (Weeks 5-6)
| Task ID | Task Description | Priority | Dependencies | Assignee | Status |
|---------|------------------|----------|--------------|----------|--------|
| T011 | LangChain integration | High | T010 | Dev | ⏳ Pending |
| T012 | CrewAI agent setup | Medium | T011 | Dev | ⏳ Pending |
| T013 | Conversational interface | High | T005, T011 | Dev | ⏳ Pending |
| T014 | Network command processing | High | T013 | Dev | ⏳ Pending |
| T015 | Configuration management | Medium | T014 | Dev | ⏳ Pending |

### Phase 4: Advanced Features (Weeks 7-8)
| Task ID | Task Description | Priority | Dependencies | Assignee | Status |
|---------|------------------|----------|--------------|----------|--------|
| T016 | Advanced audit features | Medium | T009 | Dev | ⏳ Pending |
| T017 | Configuration generation | Medium | T015 | Dev | ⏳ Pending |
| T018 | Web UI enhancement | Medium | T013 | Dev | ⏳ Pending |
| T019 | Error handling & logging | High | All previous | Dev | ⏳ Pending |
| T020 | Testing & validation | High | All previous | Dev | ⏳ Pending |

## Progress Tracking

### Overall Project Progress: 30%
- **Phase 1:** 100% Complete ✅ 
- **Phase 2:** 15% Complete ⏳
- **Phase 3:** 0% Complete ⏳
- **Phase 4:** 0% Complete ⏳

### Key Milestones
- [x] **M1:** Basic infrastructure setup (Week 2) ✅
- [ ] **M2:** Document ingestion working (Week 3) ⏳
- [ ] **M3:** Network discovery functional (Week 4) ⏳
- [ ] **M4:** RAG system operational (Week 5) ⏳
- [ ] **M5:** Conversational AI working (Week 6) ⏳
- [ ] **M6:** Configuration management ready (Week 7) ⏳
- [ ] **M7:** Full demo ready (Week 8) ⏳

### Recent Achievements
- ✅ **Fixed all database session issues** - SQLAlchemy objects properly detached
- ✅ **Working web interface** - All 5 test cases passing
- ✅ **API endpoints functional** - Health, stats, and devices endpoints working
- ✅ **Network devices initialized** - All 6 routers (R15-R20) loaded in database
- ✅ **Environment configuration** - PYTHONPATH and dependencies resolved

## Risk Assessment
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Ollama model performance | High | Medium | Test with different models, optimize prompts |
| Network device connectivity | High | Low | Implement robust error handling |
| RAG accuracy | Medium | Medium | Fine-tune embedding model, improve chunking |
| Configuration errors | High | Medium | Implement validation and rollback |

## Success Criteria
1. Successfully ingest and query network configuration documents
2. Discover and connect to network devices in specified range
3. Perform basic network audits (OSPF, BGP, ping)
4. Execute simple configuration changes via natural language
5. Provide accurate responses to network-related questions
6. Demonstrate end-to-end workflow in demo environment

## Known Network Issues (From Configs)
Based on the provided configurations, the following issues were identified:
1. **Duplex Mismatches:** Multiple CDP duplex mismatch errors between devices
2. **BGP AS Issues:** R20 has BGP AS mismatch notifications
3. **Interface Configuration:** Inconsistent duplex/speed settings across devices

## References
- Network device configurations provided
- IP range: 172.16.39.107-120
- Management network: 172.16.39.0/24
- Test devices: R15, R16, R17, R18, R19, R20

---
**Document Version:** 1.0  
**Last Updated:** 2024  
**Next Review:** Weekly during development 