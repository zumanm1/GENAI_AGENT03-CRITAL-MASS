# Network Automation AI Agent

An AI-powered network automation platform that enables natural language interaction with network devices, performs intelligent audits, and executes configuration tasks using Ollama LLM and RAG capabilities.

## 🚀 Project Overview

This project implements an **Agentic RAG system** for network automation, allowing users to:
- Chat with their network infrastructure using natural language
- Upload and query network configuration documents
- Perform automated network audits (OSPF, BGP, interface status)
- Execute basic configuration changes through AI agents
- Discover and manage network devices automatically

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   AI Agents     │    │   Network Ops   │
│   (Flask App)   │────│   (CrewAI)      │────│   (Netmiko)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG System    │    │   Vector DB     │    │   Device Mgmt   │
│   (LangChain)   │────│   (ChromaDB)    │────│   (Inventory)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Doc Ingestion │    │   LLM Engine    │    │   Config Mgmt   │
│   (PDF/Excel)   │    │   (Ollama)      │    │   (Backup/Deploy)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **LLM:** Ollama (Llama 3.1 1B)
- **RAG Framework:** LangChain + CrewAI
- **Vector Database:** ChromaDB
- **Web Framework:** Flask
- **Network Automation:** Netmiko, Nornir, PyATS/Genie
- **Document Processing:** PyPDF2, Pandas, OpenPyXL
- **Language:** Python 3.9+

## 📋 Features

### ✅ Core Features
- [x] Project structure and documentation
- [ ] Document ingestion (PDF, Excel, Text)
- [ ] Network device discovery (172.16.39.107-120)
- [ ] AI-powered chat interface
- [ ] Network audit tools (OSPF, BGP, ping)
- [ ] Configuration management
- [ ] Multi-agent system (4 specialized agents)

### 🤖 AI Agents
1. **Network Engineer Agent** - Network design and configuration
2. **Troubleshooter Agent** - Issue diagnosis and resolution
3. **Configuration Manager Agent** - Config generation and deployment
4. **Audit Agent** - Compliance and security analysis

### 🔧 Network Operations
- Device discovery and inventory
- OSPF neighbor validation
- BGP peer status checking
- Interface monitoring
- Connectivity testing
- Configuration backup/restore

## 📁 Project Structure

```
GEN_AI-AUTOMATION/
├── PRD.md                          # Main Product Requirements Document
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── config/                         # Configuration files
│   ├── app_config.py
│   ├── network_config.py
│   └── ollama_config.py
├── src/                           # Source code
│   ├── agents/                    # AI Agents (CrewAI)
│   │   ├── PRD_AGENTS.md
│   │   ├── network_engineer/
│   │   ├── troubleshooter/
│   │   ├── config_manager/
│   │   └── audit_agent/
│   ├── core/                      # Core functionality
│   │   ├── database/
│   │   ├── models/
│   │   └── config/
│   ├── network/                   # Network operations
│   │   ├── PRD_NETWORK.md
│   │   ├── discovery/
│   │   ├── audit/
│   │   └── configuration/
│   ├── rag/                       # RAG system
│   │   ├── PRD_RAG.md
│   │   ├── ingestion/
│   │   ├── processing/
│   │   └── retrieval/
│   ├── web/                       # Web interface
│   │   ├── PRD_WEB.md
│   │   ├── templates/
│   │   └── static/
│   └── utils/                     # Utilities
│       ├── logging/
│       └── validation/
├── data/                          # Data storage
│   ├── documents/                 # Uploaded documents
│   ├── logs/                      # Application logs
│   └── db/                        # Database files
├── tests/                         # Test files
└── scripts/                       # Utility scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Ollama installed and running
- Network access to devices (172.16.39.107-120)
- SSH credentials for network devices

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GEN_AI-AUTOMATION
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and setup Ollama**
   ```bash
   # Install Ollama (see https://ollama.ai)
   ollama pull llama3.1:1b
   ```

5. **Configure environment**
   ```bash
   cp config/app_config.py.example config/app_config.py
   # Edit configuration files as needed
   ```

6. **Run the application**
   ```bash
   python src/web/app.py
   ```

## 🔧 Configuration

### Network Configuration
Update `config/network_config.py` with your network details:
```python
NETWORK_RANGE = "172.16.39.107-120"
SSH_USERNAME = "cisco"
SSH_PASSWORD = "cisco"
DEVICE_TYPE = "cisco_ios"
```

### Ollama Configuration
Update `config/ollama_config.py`:
```python
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1:1b"
```

## 🎯 Usage Examples

### Chat with Network
```
User: "What's the status of OSPF on R15?"
Agent: "Let me check the OSPF status on R15... [performs audit] 
        OSPF is running with 2 neighbors in area 0."
```

### Configuration Management
```
User: "Configure interface FastEthernet0/1 on R19 with IP 192.168.1.1/24"
Agent: "I'll configure the interface for you... [generates and applies config]
        Interface configured successfully."
```

### Network Troubleshooting
```
User: "Why is there a duplex mismatch between R15 and R19?"
Agent: "I found the issue... [analyzes configurations]
        R15 has 'duplex auto' while R19 has 'duplex half'. 
        I recommend setting both to 'duplex full'."
```

## 📊 Progress Tracking

### Overall Progress: 10%
- **Phase 1 (Foundation):** 10% - Project structure created
- **Phase 2 (Core Features):** 0% - Pending
- **Phase 3 (AI Integration):** 0% - Pending  
- **Phase 4 (Advanced Features):** 0% - Pending

### Next Steps
1. ✅ Complete project structure setup
2. ⏳ Implement Ollama integration
3. ⏳ Setup ChromaDB vector database
4. ⏳ Create basic Flask application
5. ⏳ Implement document ingestion system

## 🧪 Testing

### Network Environment
The project is designed to work with the following test network:
- **R15** (172.16.39.115) - PE Router, AS 2222
- **R16** (172.16.39.116) - PE Router, AS 2222  
- **R17** (172.16.39.117) - P Router, AS 2222
- **R18** (172.16.39.118) - RR Router, AS 2222
- **R19** (172.16.39.119) - CE Router, AS 100
- **R20** (172.16.39.120) - CE Router, AS 13

### Known Issues
- Multiple duplex mismatch errors between devices
- BGP AS configuration issues on R20
- Inconsistent interface speed/duplex settings

## 🤝 Contributing

1. Check the PRD documents for task assignments
2. Follow the established project structure
3. Update progress tracking in relevant PRD files
4. Test thoroughly before committing
5. Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 References

- [Ollama Documentation](https://ollama.ai)
- [LangChain Documentation](https://langchain.readthedocs.io)
- [CrewAI Documentation](https://crewai.com)
- [Netmiko Documentation](https://netmiko.readthedocs.io)
- [ChromaDB Documentation](https://docs.trychroma.com)

---

**Project Status:** 🚧 In Development  
**Last Updated:** 2024  
**Next Review:** Weekly during development phase 