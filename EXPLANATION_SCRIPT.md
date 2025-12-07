# Langie - Explanation Script

## Introduction (30 seconds)

"Hi, I'm here to explain **Langie** - an invoice processing agent that automates the entire invoice lifecycle from intake to payment. 

Langie is built using **LangGraph**, a framework for building stateful, multi-actor applications with LLMs. What makes Langie special is its intelligent combination of automation and human oversight - it processes invoices automatically when everything matches, but intelligently pauses for human review when it detects discrepancies.

Let me walk you through how it works."

---

## Problem Statement (1 minute)

"Traditional invoice processing is manual and time-consuming. Finance teams spend hours:
- Validating invoices against purchase orders
- Checking vendor information
- Matching line items and amounts
- Generating accounting entries
- Getting approvals
- Posting to ERP systems

This is error-prone, slow, and doesn't scale well.

**Langie solves this** by automating the entire workflow while maintaining quality through intelligent human checkpoints. It processes what it can automatically, and only involves humans when there's an actual problem that needs human judgment."

---

## Solution Overview (1 minute)

"Langie is a **12-stage workflow** that processes invoices end-to-end:

**Stages 1-5: Data Collection & Validation**
- First, we intake and validate the invoice
- Then we extract text using OCR - supporting both PDF and image files
- We normalize vendor information and enrich it with credit scores
- We retrieve related purchase orders, receipts, and payment history
- Finally, we match the invoice to the purchase order

**Stage 6: Intelligent Quality Control**
- If the match is successful, we proceed automatically
- If the match fails - for example, the amount doesn't match or line items differ - we **pause the workflow** and create a human review checkpoint

**Stages 7-12: Processing & Completion**
- A human reviewer examines the invoice and makes a decision
- If accepted, we generate accounting entries
- We handle approvals - automatically for small amounts, manually for larger ones
- We post to the ERP system
- We notify the vendor and finance team
- Finally, we complete the workflow

The key insight is: **automate the routine, involve humans for the exceptions**."

---

## Architecture Deep Dive (2 minutes)

"Let me explain the technical architecture.

**Frontend Layer:**
- We have a React application that provides three main views:
  - Submit Invoice: Where users upload invoices, either as JSON or with file attachments
  - Human Review: A queue showing all invoices waiting for human decision
  - Database Preview: A comprehensive view of all processed invoices with filters and detailed audit trails

**Backend Layer:**
- A FastAPI server that exposes REST endpoints
- Handles file uploads, processes invoices, manages the review queue
- Communicates with the workflow engine

**Workflow Engine:**
- This is where LangGraph comes in
- We define a **StateGraph** - a state machine where each node represents a stage
- The graph has conditional edges that route based on results
- For example, after matching, if the match fails, we route to the HITL checkpoint

**State Management:**
- LangGraph uses a **checkpointer** - in our case, SQLite
- After each stage, the entire workflow state is persisted
- This means if the system crashes, we can resume from where we left off
- It also means we can pause for human review and resume later

**Integration Layer:**
- We have MCP clients that simulate integrations with external systems:
  - **COMMON server**: Handles vendor normalization, matching logic, and accounting entry generation
  - **ATLAS server**: Provides OCR capabilities, vendor enrichment, ERP posting, and notifications

**Tool Selection:**
- We use **Bigtool** for dynamic tool selection
- Instead of hardcoding which OCR provider to use, we select it based on capability and context
- This makes the system flexible and allows for easy swapping of providers"

---

## Key Features (2 minutes)

"Let me highlight the key features that make Langie production-ready:

**1. Human-In-The-Loop (HITL) Checkpoints**
- Workflows automatically pause when quality issues are detected
- Human reviewers get complete context - the invoice, the purchase order, the match results, everything
- Once a decision is made, the workflow automatically resumes
- All decisions are logged for audit purposes

**2. State Persistence**
- Every workflow state is saved after each stage
- This enables checkpoint and resume functionality
- It also provides a complete audit trail
- We can see exactly what happened at every stage

**3. Dynamic Tool Selection**
- Instead of hardcoding integrations, we use Bigtool to select tools dynamically
- This makes it easy to swap OCR providers, ERP systems, or other integrations
- The system adapts based on what's available

**4. File Processing**
- Users can upload invoices as PDFs or images
- The system uses OCR to extract text automatically
- Tesseract for images, PyPDF2 for PDFs
- The extracted text is then processed through the NLP pipeline

**5. Complete Observability**
- Every action is logged with structured logging
- We can see when each stage starts and ends
- We track tool selections, MCP calls, checkpoint creation
- This makes debugging and monitoring easy

**6. Typed State Management**
- We use TypedDict for our workflow state
- This provides type safety and makes the code more maintainable
- The state is a single global object that flows through all stages"

---

## How It Works - Technical Flow (2 minutes)

"Let me walk you through what happens when an invoice is submitted:

**Step 1: Submission**
- User submits invoice via the frontend or API
- Files are uploaded and saved to disk
- Invoice data is validated

**Step 2: Workflow Initialization**
- LangGraph creates a new workflow thread
- Initial state is created with the invoice payload
- First checkpoint is created

**Step 3: Stage Execution**
- Each stage is a Python function that receives the current state
- The function processes the state and returns updates
- LangGraph merges the updates into the state
- A new checkpoint is created

**Step 4: Conditional Routing**
- After certain stages, we check conditions
- For example, after MATCH_TWO_WAY, we check the match result
- If match fails, we route to CHECKPOINT_HITL
- Otherwise, we continue to the next stage

**Step 5: HITL Checkpoint (if needed)**
- When match fails, the workflow pauses
- State is saved to SQLite
- An entry is created in the human review queue
- The workflow waits for human input

**Step 6: Human Decision**
- Reviewer examines the invoice in the UI
- They see all the context - invoice, PO, match evidence
- They make a decision: ACCEPT or REJECT
- Decision is saved to both the database and workflow state

**Step 7: Resume**
- Once decision is made, the workflow resumes
- State is updated with the human decision
- The workflow continues to the next stage based on the decision
- If ACCEPT, it goes to RECONCILE
- If REJECT, it goes to COMPLETE

**Step 8: Completion**
- Workflow executes remaining stages
- Final state is saved
- Status is updated to COMPLETED
- All stages and decisions are available in the audit trail"

---

## Demo Walkthrough (3 minutes)

"Now let me show you how this works in practice. Let's run through a complete demo:

**Scenario 1: Auto-Complete (No HITL)**
- I'm submitting an invoice from Acme Corp for $1000
- This matches an existing purchase order
- The workflow processes it automatically through all 12 stages
- Notice: No human intervention needed
- Status shows COMPLETED in the database preview
- This is the happy path - routine invoices process automatically

**Scenario 2: HITL Triggered**
- Now I'm submitting an invoice from Beta Industries for $6000
- This doesn't match any purchase order
- The match stage detects the discrepancy
- The workflow automatically pauses at the CHECKPOINT_HITL stage
- Look at the Human Review tab - the invoice appears in the pending queue
- Status shows PAUSED
- This is where human judgment is needed

**Scenario 3: Human Review**
- I click on the review button
- I can see the complete invoice details
- I can see what purchase orders were considered
- I can see why the match failed - the amount difference is $5000
- After reviewing, I select ACCEPT
- The system automatically generates a reviewer ID
- I submit the decision

**Scenario 4: Auto-Resume**
- Once I submit ACCEPT, the workflow automatically resumes
- It proceeds to RECONCILE stage, generating accounting entries
- Then APPROVE, POSTING, NOTIFY, and finally COMPLETE
- If I check the database preview, I can see:
  - Status is now COMPLETED
  - Decision shows ACCEPT
  - All stages are visible with their outputs
  - Complete audit trail is available

**Database Preview**
- This is the comprehensive view of all processed invoices
- I can filter by status: Pending, Accepted, Rejected, or Completed
- Each invoice shows:
  - Complete workflow state
  - All stage outputs
  - Human decisions
  - Timestamps
  - Full audit trail"

---

## Code Architecture (2 minutes)

"Let me briefly explain the code structure:

**Workflow Configuration**
- `workflow.json` defines all 12 stages, their modes, tools, and output schemas
- This is our single source of truth for the workflow definition

**State Models**
- `src/state/models.py` defines TypedDict models for each stage output
- `WorkflowState` is the global state that flows through all stages
- Each stage has a specific output type that gets merged into the state

**Graph Builder**
- `src/graph/builder.py` constructs the LangGraph StateGraph
- It adds all 12 nodes
- It defines the edges - both sequential and conditional
- It compiles the graph with the SQLite checkpointer

**Node Functions**
- Each stage has its own node function in `src/nodes/`
- Nodes receive state and return updates
- They're wrapped with runtime context for dependency injection
- This keeps nodes testable and reusable

**API Layer**
- `src/api/app.py` exposes REST endpoints
- Handles file uploads with multipart/form-data
- Manages the human review queue
- Integrates with the workflow graph

**Frontend**
- React components for each view
- InvoiceSubmit handles file uploads
- HumanReview shows pending reviews and accepts decisions
- DatabasePreview shows all workflows with filters and details"

---

## Real-World Benefits (1 minute)

"Let me explain why this matters:

**For Finance Teams:**
- **Speed**: Routine invoices process in seconds instead of hours
- **Accuracy**: Automated matching reduces human error
- **Focus**: Humans only review exceptions, not routine cases
- **Audit**: Complete trail for compliance

**For Organizations:**
- **Scalability**: Process hundreds of invoices without hiring more staff
- **Cost**: Reduce manual processing costs significantly
- **Quality**: Consistent processing with quality checkpoints
- **Insights**: Full visibility into invoice processing metrics

**For Developers:**
- **Flexibility**: Easy to modify workflow stages
- **Maintainability**: Clear separation of concerns
- **Testability**: Each component is independently testable
- **Observability**: Structured logging for debugging"

---

## Technical Highlights (1 minute)

"What makes this technically interesting:

**LangGraph Patterns:**
- We use StateGraph for workflow orchestration
- Conditional routing based on state
- Checkpoint persistence for reliability
- State machine patterns for complex workflows

**State Management:**
- Single global state object (TypedDict)
- Type-safe state updates
- Complete state persistence
- State merging for incremental updates

**HITL Implementation:**
- Native checkpoint pause/resume
- State isolation per workflow thread
- Human decision integration
- Automatic workflow resumption

**Dynamic Tool Selection:**
- Bigtool for capability-based selection
- Easy to add new tools
- Provider abstraction
- Context-aware selection"

---

## Conclusion (30 seconds)

"In summary, **Langie demonstrates**:
- Production-ready invoice processing with LangGraph
- Intelligent automation with human oversight
- Complete state persistence and audit trails
- Flexible architecture with dynamic tool selection
- Full-stack application with React frontend and FastAPI backend

The system is **ready for deployment** and can be extended with:
- Authentication and authorization
- Multi-tenant support
- Advanced ML-based matching
- Integration with real ERP systems
- Custom business rules

Thank you for your attention. I'm happy to answer any questions!"

---

## Q&A Preparation

### Common Questions:

**Q: How does this compare to commercial solutions?**
A: Langie is a reference implementation demonstrating LangGraph capabilities. It's designed to be customizable and extensible. Commercial solutions might have more features, but Langie shows how you can build your own with full control.

**Q: What if the OCR fails?**
A: The system includes fallback mechanisms. If OCR fails, it uses the invoice data provided directly. The workflow continues, but flags the issue for review.

**Q: How does it handle edge cases?**
A: The workflow includes validation at each stage. Invalid data is flagged and routed appropriately. The HITL checkpoint catches issues that automated processing might miss.

**Q: Can this scale to thousands of invoices?**
A: Yes. The architecture supports horizontal scaling. The SQLite database can be upgraded to PostgreSQL for better concurrency. The async FastAPI backend handles multiple requests efficiently.

**Q: How do you ensure data security?**
A: The current implementation focuses on workflow orchestration. Production deployment should add authentication, encryption, and access controls. The architecture supports these additions.

**Q: What about integration with our ERP?**
A: The MCP client architecture allows easy integration. You would implement the ATLAS server interface for your specific ERP system. The workflow code remains unchanged.

---

## Timing Breakdown

- Introduction: 30 seconds
- Problem Statement: 1 minute
- Solution Overview: 1 minute
- Architecture Deep Dive: 2 minutes
- Key Features: 2 minutes
- Technical Flow: 2 minutes
- Demo Walkthrough: 3 minutes
- Code Architecture: 2 minutes
- Real-World Benefits: 1 minute
- Technical Highlights: 1 minute
- Conclusion: 30 seconds

**Total: ~16-17 minutes**

---

## Delivery Tips

1. **Pace yourself**: Don't rush. The script is ~17 minutes, but with pauses and questions, plan for 20-25 minutes.

2. **Use visuals**: When describing architecture, refer to diagrams. When demonstrating, show the actual UI.

3. **Emphasize key points**: 
   - "Automatic pause on exceptions"
   - "State persistence"
   - "Human-in-the-loop"
   - "Complete audit trail"

4. **Interactive demo**: If possible, let the audience suggest scenarios. Show how the system handles edge cases.

5. **Be ready for questions**: Have the architecture details ready. Know where things are in the code.

6. **Show the code**: If appropriate, quickly show key files like workflow.json or a node function to demonstrate simplicity.

---

**Good luck with your presentation!** 🚀

