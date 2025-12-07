# Langie - Video/Recording Script

## Scene 1: Introduction (0:00 - 0:30)

**[Screen: Logo/Title: "Langie - Invoice Processing Agent"]**

"Welcome! I'm here to show you **Langie**, an intelligent invoice processing system built with LangGraph.

Langie automates the entire invoice lifecycle - from when an invoice arrives, through validation, matching, approval, all the way to payment. But here's what makes it special: it combines **automation with intelligence**. It processes routine invoices automatically, but automatically pauses for human review when something doesn't match.

Let me show you how it works."

**[Transition: Fade to system diagram]**

---

## Scene 2: The Problem (0:30 - 1:30)

**[Screen: Show traditional invoice processing - lots of paperwork, manual steps]**

"Traditional invoice processing is slow and manual. Finance teams spend hours:
- Matching invoices to purchase orders
- Checking vendor information
- Validating amounts and line items
- Getting approvals
- Posting to ERP systems

This is error-prone and doesn't scale. As businesses grow, invoice volume grows, but you can't just keep hiring more finance staff.

**[Screen: Show automation vs manual]**

Langie solves this by automating what can be automated, and intelligently involving humans only when their judgment is truly needed."

**[Transition: Animate to solution]**

---

## Scene 3: The Solution (1:30 - 2:30)

**[Screen: Show workflow diagram with 12 stages]**

"Langie processes invoices through 12 automated stages:

**First, data collection:**
- We intake and validate the invoice
- Extract text using OCR - supporting PDFs and images
- Normalize vendor information
- Retrieve purchase orders and payment history
- Match the invoice to the purchase order

**Then, intelligent quality control:**
- If everything matches, we proceed automatically
- If something doesn't match, we pause and create a human review checkpoint

**Finally, processing:**
- After human approval, we generate accounting entries
- Handle approvals
- Post to ERP
- Notify stakeholders
- Complete the workflow

**[Screen: Highlight HITL checkpoint]**

The key is: automate the routine, involve humans for the exceptions."

**[Transition: Show architecture]**

---

## Scene 4: Architecture Overview (2:30 - 4:00)

**[Screen: Architecture diagram]**

"Let me explain the technical architecture:

**Frontend**: A React application with three main views - submit invoices, review pending items, and view all processed invoices.

**Backend**: FastAPI server handling requests and file uploads.

**Workflow Engine**: LangGraph orchestrates the entire process. We define a state machine where each node is a processing stage.

**State Management**: After every stage, the complete state is saved to SQLite. This means we can pause, resume, or even recover from crashes.

**Integration Layer**: MCP clients simulate external systems - OCR, ERP, vendor databases. The system uses dynamic tool selection to choose the right tool for each task.

**[Screen: Highlight state persistence]**

This architecture is production-ready - scalable, observable, and reliable."

**[Transition: Show demo UI]**

---

## Scene 5: Live Demo - Part 1 (4:00 - 6:00)

**[Screen: Frontend UI - Submit Invoice tab]**

"Let me show you how this works in practice.

**First, let's submit an invoice that will process automatically:**

**[Action: Fill in invoice form]**
- Invoice ID: INV-DEMO-001
- Vendor: Acme Corp
- Amount: $1000
- This matches an existing purchase order

**[Action: Click Submit]**

**[Screen: Show workflow processing - stage by stage]**

Watch as it processes:
- INTAKE: Validated
- UNDERSTAND: Text extracted
- PREPARE: Vendor normalized
- RETRIEVE: PO found
- MATCH: Match successful
- RECONCILE: Accounting entries created
- APPROVE: Auto-approved
- POSTING: Posted to ERP
- NOTIFY: Notifications sent
- COMPLETE: Done!

**[Screen: Show completed status in Database Preview]**

Notice - no human intervention needed. Status is COMPLETED. This is the happy path."

**[Transition: Show HITL scenario]**

---

## Scene 6: Live Demo - Part 2 (6:00 - 8:00)

**[Screen: Submit another invoice]**

"Now let's see what happens when something doesn't match:

**[Action: Submit invoice with $6000 amount]**
- Invoice ID: INV-DEMO-002
- Vendor: Beta Industries
- Amount: $6000
- This doesn't match any purchase order

**[Action: Click Submit]**

**[Screen: Show workflow processing, then pause]**

The workflow processes through the stages:
- INTAKE: Validated
- UNDERSTAND: Text extracted
- PREPARE: Vendor normalized
- RETRIEVE: PO found, but amount doesn't match
- MATCH: Match failed - amount difference too large
- **CHECKPOINT_HITL: Workflow PAUSED**

**[Screen: Show Human Review tab with pending invoice]**

Look at the Human Review tab - the invoice appears automatically. Status shows PAUSED. The system detected the issue and paused for human review."

**[Transition: Show review interface]**

---

## Scene 7: Live Demo - Part 3 (8:00 - 9:30)

**[Screen: Human Review interface]**

"Let's review this invoice:

**[Action: Click Review button]**

I can see:
- Complete invoice details
- The purchase order that was considered
- Why the match failed - amount difference is $5000
- All the context needed to make a decision

**[Action: Select ACCEPT, add notes, click Submit]**

After reviewing, I select ACCEPT and submit.

**[Screen: Show workflow resuming automatically]**

Watch what happens next - the workflow automatically resumes:
- HITL_DECISION: Decision recorded
- RECONCILE: Accounting entries generated
- APPROVE: Approved
- POSTING: Posted to ERP
- NOTIFY: Notifications sent
- COMPLETE: Done!

**[Screen: Show completed status with ACCEPT decision]**

The system automatically resumed and completed. Status shows COMPLETED, Decision shows ACCEPT. All actions are logged for audit."

**[Transition: Show Database Preview]**

---

## Scene 8: Database Preview (9:30 - 10:30)

**[Screen: Database Preview tab]**

"Let me show you the comprehensive audit trail:

**[Action: Show all invoices, filters]**

The Database Preview shows all processed invoices. I can filter by:
- All invoices
- Pending - waiting for review
- Accepted - human approved
- Rejected - human rejected
- Completed - all completed workflows

**[Action: Click View Details on an invoice]**

Each invoice shows:
- Complete workflow state
- All 12 stage outputs
- Human decisions
- Timestamps
- Full audit trail

**[Screen: Highlight audit trail details]**

This provides complete visibility and compliance."

**[Transition: Show code/architecture]**

---

## Scene 9: Technical Highlights (10:30 - 12:00)

**[Screen: Show workflow.json or code snippets]**

"Let me highlight what makes this technically interesting:

**LangGraph State Machine**: We define the workflow as a state machine with conditional routing.

**[Screen: Show state models]**

**Typed State**: Every stage has a typed output that gets merged into a global state object.

**[Screen: Show checkpoint code]**

**State Persistence**: After every stage, state is saved. This enables pause, resume, and recovery.

**[Screen: Show HITL node]**

**Human-In-The-Loop**: Native support for pausing workflows and resuming after human input.

**[Screen: Show MCP clients]**

**Flexible Integration**: MCP clients abstract external systems, making it easy to integrate with different ERPs or OCR providers.

This architecture is production-ready and extensible."

**[Transition: Show benefits]**

---

## Scene 10: Benefits & Use Cases (12:00 - 13:00)

**[Screen: Benefits list]**

"Here's why this matters:

**For Finance Teams:**
- Process routine invoices in seconds, not hours
- Focus human time on exceptions, not routine work
- Complete audit trail for compliance

**For Organizations:**
- Scale invoice processing without scaling staff
- Reduce processing costs
- Maintain quality through intelligent checkpoints

**For Developers:**
- Clean, maintainable architecture
- Easy to extend and customize
- Full observability for debugging

**[Screen: Use cases]**
- High-volume invoice processing
- Multi-vendor scenarios
- Compliance-heavy industries
- Integration with existing ERP systems"

**[Transition: Conclusion]**

---

## Scene 11: Conclusion (13:00 - 13:30)

**[Screen: Summary slide]**

"In summary, **Langie demonstrates**:
- Production-ready invoice processing with LangGraph
- Intelligent automation with human oversight
- Complete state persistence and audit trails
- Flexible, extensible architecture

The system is ready for deployment and can be extended with authentication, multi-tenant support, advanced ML matching, and real ERP integrations.

**[Screen: Call to action]**

Check out the code, try the demo, and see how you can build intelligent automation workflows with LangGraph.

Thank you for watching!"

**[Screen: End screen with links/resources]**

---

## Production Notes

### Visuals Needed:
1. System architecture diagram
2. Workflow stage diagram
3. State flow diagram
4. HITL checkpoint flow
5. Code snippets (workflow.json, node functions)
6. UI screenshots/recordings

### Transitions:
- Smooth fade between scenes
- Animate diagrams when explaining
- Highlight relevant parts during demo
- Use zoom/pan for code screenshots

### Timing:
- Total length: ~13-14 minutes
- Keep each scene tight and focused
- Allow natural pauses for emphasis
- Use background music (optional, low volume)

### Voiceover Tips:
- Speak clearly and at moderate pace
- Emphasize key concepts (automation, HITL, state persistence)
- Use intonation to show excitement for cool features
- Pause after important points

---

**Ready for recording!** 🎬

