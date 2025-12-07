# Langie - 4-Minute Video Script

## 🎬 Complete Video Script (4:00)

---

## Scene 1: Introduction (0:00 - 0:30)

**[Screen: Show Langie logo/title screen]**

"Hi! I'm [Your Name], and today I'm presenting **Langie** - an intelligent invoice processing agent built with LangGraph.

Langie automates invoice processing from intake to payment, using a **12-stage workflow** with intelligent human oversight. The key innovation? It processes routine invoices automatically, but automatically pauses for human review when it detects discrepancies.

Let me show you how it works."

**[Transition: Fade to frontend UI]**

---

## Scene 2: Problem & Solution (0:30 - 1:00)

**[Screen: Show invoice processing dashboard]**

"Traditional invoice processing is manual and slow. Finance teams spend hours matching invoices to purchase orders, checking amounts, and getting approvals.

**[Screen: Highlight workflow stages diagram]**

Langie solves this with automation plus intelligence. It has 12 automated stages that handle everything - from OCR extraction, to vendor matching, to accounting entries. But here's the smart part: if something doesn't match, it automatically pauses and asks a human to review.

**[Screen: Show HITL checkpoint flow]**

This gives us the best of both worlds - speed for routine cases, and human judgment for exceptions."

**[Transition: Switch to invoice submission]**

---

## Scene 3: Live Demo - Auto-Complete (1:00 - 2:00)

**[Screen: Invoice Submission form]**

"Let me demonstrate with a real example.

**[Action: Fill form with invoice data]**

I'm submitting an invoice from Acme Corp for $1000. This matches an existing purchase order, so it should process automatically.

**[Action: Click Submit]**

**[Screen: Show workflow processing - stage progression]**

Watch as it processes through the stages:
- **INTAKE**: Validates the invoice
- **UNDERSTAND**: Extracts text using OCR
- **PREPARE**: Normalizes vendor information
- **RETRIEVE**: Finds the matching purchase order
- **MATCH**: Calculates match score - 100% match!
- **RECONCILE**: Generates accounting entries
- **APPROVE**: Auto-approved
- **POSTING**: Posted to ERP
- **NOTIFY**: Notifications sent
- **COMPLETE**: Done!

**[Screen: Show Database Preview - completed invoice]**

Notice - no human intervention needed. Status shows **COMPLETED**, and the decision column shows **"Completed (No Review Needed)"**. 

This invoice processed in seconds, automatically. That's the power of automation."

**[Transition: Show another invoice]**

---

## Scene 4: Live Demo - HITL Trigger (2:00 - 3:30)

**[Screen: Submit another invoice]**

"Now let's see what happens when something doesn't match.

**[Action: Submit invoice with $6000 - doesn't match PO]**

I'm submitting an invoice for $6000. This doesn't match any purchase order, so the match score will be low.

**[Action: Click Submit]**

**[Screen: Show workflow processing, then pause]**

The workflow processes through the early stages, but when it reaches **MATCH**, it detects a problem - the amount difference is too large, match score is below threshold.

**[Screen: Show Human Review tab with pending invoice]**

Automatically, the workflow pauses at **CHECKPOINT_HITL** and creates a human review entry. Notice it appears in the Human Review queue automatically.

**[Screen: Click Review button]**

Let me review this invoice:

**[Screen: Show review interface with details]**

I can see the invoice details, the purchase order that was considered, and why the match failed - amount difference of $5000. I have all the context I need.

**[Action: Select ACCEPT, add notes, submit]**

After reviewing, I select **ACCEPT** and submit.

**[Screen: Show workflow automatically resuming]**

Watch what happens - the workflow automatically resumes:
- **HITL_DECISION**: Decision recorded
- **RECONCILE**: Accounting entries created
- **APPROVE**: Approved
- **POSTING**: Posted to ERP
- **NOTIFY**: Notifications sent
- **COMPLETE**: Done!

**[Screen: Show completed status]**

The system detected the issue, paused for human judgment, and automatically resumed after the decision. This is intelligent automation."

**[Transition: Show Database Preview]**

---

## Scene 5: Features & Capabilities (3:30 - 3:50)

**[Screen: Database Preview with filters and sorting]**

"Let me show you the comprehensive audit trail:

**[Action: Show filters and sorting]**

The Database Preview shows all processed invoices. I can filter by status - All, Pending, Accepted, Rejected, or Completed. I can sort by date, amount, vendor, or status.

**[Action: Click on an invoice to show details]**

Each invoice shows complete workflow details - all 12 stage outputs, decisions, timestamps - everything for compliance and auditing.

**[Screen: Highlight key features]**

Key features:
- **File upload** with OCR for PDF and images
- **Automatic pause** on discrepancies
- **Auto-resume** after human decision
- **Complete audit trail**
- **Sorting and filtering**
- **Delete functionality** for workflow management"

**[Transition: Architecture diagram]**

---

## Scene 6: Conclusion (3:50 - 4:00)

**[Screen: Summary slide]**

"In summary, **Langie demonstrates**:
- Production-ready invoice processing with LangGraph
- 12-stage automated workflow
- Intelligent human-in-the-loop checkpoints
- Complete state persistence and audit trails
- Full-stack application with React and FastAPI

The system is ready for deployment and can be extended with authentication, multi-tenant support, and real ERP integrations.

Thank you for watching!"

**[Screen: End screen with contact/project info]**

---

## 📋 Production Notes

### Timing Breakdown
- **Introduction**: 30 seconds
- **Problem & Solution**: 30 seconds
- **Auto-Complete Demo**: 1 minute
- **HITL Demo**: 1 minute 30 seconds
- **Features**: 20 seconds
- **Conclusion**: 10 seconds
- **Total**: 4 minutes

### Visual Cues

#### Screen Recordings Needed:
1. **Invoice Submission Form** - Fill and submit
2. **Workflow Processing** - Show stage progression (can be speed-up animation)
3. **Human Review Queue** - Show pending invoice
4. **Review Interface** - Show decision submission
5. **Database Preview** - Show filters, sorting, details

#### Key Highlights:
- ✅ **Emphasize**: "Automatically pauses" / "Automatically resumes"
- ✅ **Show**: Match score calculation
- ✅ **Highlight**: "No Review Needed" vs "ACCEPT" decisions
- ✅ **Demonstrate**: Sorting and filtering capabilities

### Voiceover Tips

1. **Pace**: Speak clearly but keep a steady pace (4 minutes is tight)
2. **Emphasis**: 
   - "Automatically" (key differentiator)
   - "12-stage workflow"
   - "Intelligent automation"
3. **Transitions**: Use phrases like "Let me show you...", "Notice...", "Watch..."
4. **Energy**: Keep enthusiasm up, especially during demo sections

### What to Show

#### Must-Have Shots:
1. ✅ Submit invoice → Auto-complete (no HITL)
2. ✅ Submit invoice → HITL triggered → Human review → Auto-resume
3. ✅ Database Preview with filters and sorting
4. ✅ Workflow details showing all stages

#### Nice-to-Have:
- File upload demonstration
- OCR processing visualization
- Backend logs (if shown on screen)

---

## 🎯 Key Messages

1. **Automation + Intelligence**: Not just automation, but smart automation that knows when to pause
2. **12-Stage Workflow**: Comprehensive end-to-end processing
3. **Human-In-The-Loop**: Seamless integration of human judgment
4. **Production-Ready**: Complete audit trail, state persistence, error handling
5. **Full-Stack**: React frontend + FastAPI backend + LangGraph orchestration

---

## 📝 Alternative Shorter Version (if 4 min is tight)

If you need to cut time, focus on:
- **Introduction**: 20s
- **Auto-Complete Demo**: 1m 20s (show this is the happy path)
- **HITL Demo**: 1m 50s (show the intelligence)
- **Quick Features**: 15s
- **Conclusion**: 15s

**Total: 4:00**

---

**Ready for recording!** 🎬

