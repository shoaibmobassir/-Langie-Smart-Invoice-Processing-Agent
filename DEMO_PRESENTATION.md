# Langie Demo - Presentation Guide

## 🎯 Executive Summary

**Langie** is a production-ready invoice processing agent built with LangGraph that demonstrates:
- **12-stage automated workflow** from invoice intake to payment
- **Intelligent Human-In-The-Loop (HITL)** checkpoints for quality control
- **Dynamic tool selection** for flexible integrations
- **Full state persistence** with checkpoint & resume capabilities
- **Complete audit trail** for compliance and debugging

---

## 🏗️ Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ React UI    │─────▶│ FastAPI API  │─────▶│ LangGraph   │
│ (Frontend)  │      │ (Backend)    │      │ Workflow    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ├──────────┐           │
                            ▼          ▼           │
                    ┌──────────┐ ┌──────────┐     │
                    │ SQLite   │ │ MCP      │     │
                    │ Database │ │ Clients  │     │
                    └──────────┘ └──────────┘     │
                                                  │
                                    ┌─────────────┘
                                    ▼
                            ┌──────────────┐
                            │   Bigtool    │
                            │   Selection  │
                            └──────────────┘
```

**Key Components:**
- **Frontend**: React + Vite (modern, responsive UI)
- **Backend**: FastAPI (RESTful API with async support)
- **Workflow Engine**: LangGraph (state machine orchestration)
- **Persistence**: SQLite (checkpoints + human review queue)
- **Integration**: MCP clients (COMMON & ATLAS servers)

---

## 📊 12-Stage Workflow

### Stage Flow:
```
INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH_TWO_WAY
                              ↓ (if match fails)
                    CHECKPOINT_HITL ← (Human Review)
                              ↓ (if ACCEPT)
                    HITL_DECISION → RECONCILE → APPROVE → 
                    POSTING → NOTIFY → COMPLETE
```

### Key Stages:

1. **INTAKE** - Validate and persist invoice
2. **UNDERSTAND** - OCR extraction + NLP parsing (supports PDF/image)
3. **PREPARE** - Vendor normalization + enrichment
4. **RETRIEVE** - Fetch PO, GRN, payment history
5. **MATCH_TWO_WAY** - Match invoice to PO (tolerance-based)
6. **CHECKPOINT_HITL** - Pause for human review (if match fails)
7. **HITL_DECISION** - Process human decision (ACCEPT/REJECT)
8. **RECONCILE** - Generate accounting entries
9. **APPROVE** - Approval policies (auto-approve < $10K)
10. **POSTING** - Post to ERP system
11. **NOTIFY** - Notify vendor + finance team
12. **COMPLETE** - Finalize workflow

---

## 🎬 Live Demo Flow

### 1️⃣ **Auto-Complete Scenario** (30 seconds)
**Goal:** Show fully automated processing

- Submit invoice with matching PO
- Workflow completes automatically
- **Result:** Status = "COMPLETED" without human intervention

**Key Points:**
- ✅ Match score passes threshold
- ✅ No HITL checkpoint triggered
- ✅ All 12 stages execute automatically

---

### 2️⃣ **HITL Trigger Scenario** (1 minute)
**Goal:** Show intelligent pause for quality control

- Submit invoice with non-matching amount
- Match fails → Workflow pauses
- **Result:** Invoice appears in Human Review queue

**Key Points:**
- ⏸️ Workflow automatically pauses at CHECKPOINT_HITL
- 📋 State persisted in SQLite checkpoint
- 🔍 Complete context available for reviewer

---

### 3️⃣ **Human Decision & Resume** (1 minute)
**Goal:** Show seamless human interaction

- Reviewer examines invoice details
- Selects ACCEPT or REJECT
- **Result:** Workflow automatically resumes and completes

**Key Points:**
- 👤 Reviewer ID auto-generated
- 🔄 Workflow resumes automatically after decision
- ✅ Complete audit trail maintained

---

### 4️⃣ **Database Preview** (30 seconds)
**Goal:** Show comprehensive audit trail

- View all processed invoices
- Filter by status (Pending, Accepted, Completed)
- View detailed stage-by-stage information

**Key Points:**
- 📊 Complete visibility into all workflows
- 🔍 Filter by status, decision, date
- 📝 Full audit trail with timestamps

---

## 💡 Key Features Highlighted

### ✅ **Intelligent Routing**
- Conditional edges based on match results
- Automatic HITL triggering on match failure
- Seamless resume after human decision

### ✅ **State Management**
- Single global state object (TypedDict)
- Complete state persistence (SQLite)
- Checkpoint & resume capabilities

### ✅ **Human-In-The-Loop (HITL)**
- Automatic pause on quality issues
- Rich context for human reviewers
- Auto-resume after decision
- Complete audit trail

### ✅ **Dynamic Tool Selection (Bigtool)**
- Tool selection based on capability
- OCR provider selection (Tesseract)
- ERP integration selection

### ✅ **File Processing**
- PDF upload support
- Image OCR (PNG, JPG, etc.)
- Automatic text extraction

### ✅ **Observability**
- Structured logging (structlog)
- Complete execution logs
- State snapshots at each stage

---

## 📈 Metrics & Performance

### Workflow Execution:
- **Auto-complete**: ~2-3 seconds (12 stages)
- **HITL flow**: Pauses at checkpoint, resumes in ~1 second after decision
- **State persistence**: < 100ms per checkpoint

### Scalability:
- ✅ SQLite database (can be upgraded to PostgreSQL)
- ✅ Async FastAPI (handles concurrent requests)
- ✅ Stateless nodes (easy to scale horizontally)

---

## 🔧 Technical Stack

### Backend:
- **Python 3.11+**
- **LangGraph** - Workflow orchestration
- **FastAPI** - REST API framework
- **SQLite** - Checkpoint persistence
- **structlog** - Structured logging

### Frontend:
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client

### Integrations:
- **MCP Clients** - COMMON & ATLAS servers
- **Bigtool** - Dynamic tool selection
- **Tesseract OCR** - Image text extraction
- **PyPDF2** - PDF text extraction

---

## 🎯 Use Cases

### 1. **Fully Automated Processing**
- High-confidence invoices (matching PO)
- Auto-completes without human intervention
- Fast turnaround time

### 2. **Quality Control**
- Discrepancies trigger HITL
- Human reviewers can investigate
- Maintains accuracy while automating routine cases

### 3. **Audit & Compliance**
- Complete audit trail
- All decisions logged
- Full state history available

---

## 🚀 Next Steps / Enhancements

### Potential Improvements:
1. **Multi-tenant support** - Separate workspaces/tenants
2. **Advanced matching** - ML-based matching algorithms
3. **Batch processing** - Process multiple invoices in parallel
4. **Custom rules** - User-defined matching rules
5. **Notifications** - Email/Slack integration
6. **Dashboard** - Real-time metrics and analytics

---

## 📝 Demo Checklist

- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:5173)
- [ ] Test data prepared
- [ ] Demo scenarios tested
- [ ] Logs accessible
- [ ] API docs available (http://localhost:8000/docs)

---

## 🎤 Talking Points

### Opening:
> "Langie demonstrates production-ready invoice processing with intelligent automation and human oversight. Let me show you how it works..."

### During Demo:
> "Notice how the workflow automatically pauses when it detects a discrepancy, giving human reviewers full context to make informed decisions..."

### Closing:
> "This demonstrates a complete, production-ready system with state persistence, human-in-the-loop capabilities, and full observability - all built with LangGraph."

---

## 📞 Questions & Answers

### Q: What happens if the backend crashes?
**A:** All state is persisted in SQLite checkpoints. When restarted, workflows can resume from the last checkpoint.

### Q: How does HITL scale?
**A:** The system can handle multiple reviewers processing different invoices concurrently. Each review is independent and state is isolated per workflow thread.

### Q: Can this integrate with our ERP?
**A:** Yes. The MCP client architecture allows easy integration with any ERP system through the ATLAS server interface.

### Q: What about security?
**A:** The system can be enhanced with authentication, authorization, and encryption. The current demo focuses on workflow orchestration.

---

## 📚 Additional Resources

- **DEMO_GUIDE.md** - Complete step-by-step guide
- **QUICK_DEMO.md** - Quick reference
- **README.md** - Full technical documentation
- **workflow.json** - Workflow configuration

---

**Ready to demo!** 🚀

