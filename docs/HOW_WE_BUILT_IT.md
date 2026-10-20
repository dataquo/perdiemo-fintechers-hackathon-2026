# How We Built PerDiemo

## Inspiration

Corporate travel expense processing is broken:

1. **Manual burden** - Accountants spend hours reviewing receipts, matching against declarations
2. **Complex legislation** - Czech Labour Code §§ 151-189 has multi-tiered per diem rules, meal deductions (70%/35%/25%), daily CNB exchange rates
3. **Fraud risk** - Meal double-dipping (hotel includes breakfast but employee claims it separately) is common
4. **Audit liability** - Under Czech law (NSS 3 Afs 97/2025-71), employers bear the burden of proof

**We asked:** Can AI automate this entire workflow while catching fraud?

## The Solution

PerDiemo is an autonomous document processing pipeline:

```
Upload Receipts → AI Extraction → Statutory Calculation → Compliance Audit → Verified Report
```

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Document       │     │  PerDiemo       │     │  KB Compliance  │
│  Intake         │────▶│  Statutory API  │────▶│  Rules Engine   │
│  (Bedrock)      │     │  (Cloud)        │     │  (Python)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Extract dates,         Calculate per         Check for fraud,
   hotels, meals          diems, CNB FX         anomalies, missing
   from PDFs/images       rates, deductions     declarations
```

## Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Document Extraction | AWS Bedrock (Claude Sonnet 4.5) | Multimodal - reads PDFs and images |
| Statutory Engine | PerDiemo REST API | Pre-built Czech labour code compliance |
| Compliance Rules | Python rule engine | Configurable, auditable |
| Frontend | Streamlit | Rapid prototyping for hackathon |
| PDF Generation | ReportLab | Synthetic demo documents |

## Key Technical Decisions

### 1. LLM for Extraction Only

The LLM (Claude) **only** extracts structured data from documents. It does NOT:
- Calculate per diems (hallucination risk with math)
- Make compliance decisions (must be deterministic)
- Apply exchange rates (needs exact CNB daily rates)

**Why:** LLMs hallucinate on complex Czech legislative nuances. We use a deterministic engine for calculations.

### 2. Cryptographic Audit Seal

Every calculation includes a SHA-256 signature:
```
verification_signature: "1baebc05f2cab245d5901de7a1d8447d..."
```

**Why:** Czech Supreme Administrative Court (NSS 3 Afs 97/2025-71) requires employers to prove calculation integrity during tax audits.

### 3. EU Bedrock Configuration

Model ID must use `eu.` prefix:
```
eu.anthropic.claude-sonnet-4-5-20250929-v1:0
```

**Why:** AWS European regions require EU cross-region inference profiles. Bare `anthropic.claude-*` IDs fail with ValidationException.

## Compliance Rules

| Rule ID | Detection | Risk Score |
|---------|-----------|------------|
| KB-RULE-01 | Meal double-dipping (hotel breakfast not declared) | +45 CRITICAL |
| KB-RULE-02 | Weekend travel without business justification | +25 WARNING |
| KB-RULE-03 | Missing SHA-256 audit signature | +50 CRITICAL |
| KB-RULE-04 | Corporate card transaction reconciliation | INFO |
| KB-RULE-05 | 2-Way Invoice vs Card Cross-Reconciliation | +35 CRITICAL / WARNING |

**Verdict thresholds:**
- Risk < 40 → APPROVED
- Risk 40-69 → FLAGGED_FOR_REVIEW
- Risk ≥ 70 → REJECTED

## What We Built During the Hackathon

1. **Document upload & extraction pipeline** - PDF/image → structured JSON
2. **Multi-document package processing** - Upload multiple receipts at once
3. **Natural language input** - Describe trip in text, AI extracts itinerary
4. **Fraud simulation toggle** - Demo the double-dipping detection
5. **Synthetic demo documents** - Realistic PDFs for presentation
6. **2-Way Invoice vs Banking Reconciliation Engine (Tab 4)** - Automated cross-check of OCR invoices against TSYS corporate card streams with tip tolerance, out-of-pocket settlement, orphan card flagging, and 1-click manager remediation
7. **Polished Streamlit UI** - 4-tab executive dashboard with Bedrock Sonnet 4.5 conversational payment ops and MoroSystems instant settlement sandbox

## Use Cases

### Primary: KB Back-Office Teams
- Automate receipt verification for corporate clients
- Reduce manual review time by 80%
- Catch fraud before reimbursement

### Secondary: Corporate Finance
- Employee self-service expense submission
- Real-time compliance feedback
- Audit-ready documentation

### Future: Open Banking Integration
- Match expenses against KB corporate card transactions
- Automatic receipt-to-transaction reconciliation

## Challenges Faced

1. **PDF extraction quality** - Solved with PyPDF text extraction + Bedrock fallback
2. **Complex Czech per diem rules** - Used PerDiemo API (pre-built statutory engine)
3. **Demo data** - Created synthetic documents with ReportLab
4. **AWS region constraints** - Learned about EU inference profiles the hard way

## What's Next

- Integration with KB Open Banking API for card matching
- Support for more document types (train tickets, car rentals)
- Batch processing for month-end expense runs
- Mobile receipt capture via WhatsApp/SMS (Infobip integration)
