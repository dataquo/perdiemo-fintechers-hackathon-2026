---
title: "Track 6 · Finance operations and back-office AI"
source_notion_id: "3fc1e819-9813-81ac-a1de-e622dffb3575"
source_url: "https://thefintechers.notion.site/3fc1e819981381aca1dee622dffb3575"
fetched_at: "2026-10-19T19:11:09.399Z"
category: "track"
---

# Track 6 · Finance operations and back-office AI

> 🧾

**Agents for the CFO's office.** Receivables, treasury and the legacy code nobody dares to touch.


### 🧭 At a glance


| 🤝 Partners | ⭐ Komerční banka (partner challenge), Deloitte, AWS |
| --- | --- |
| 🗄️ Data | Synthetic ERP and multi-currency position data, a legacy code sample, TSYS data. For 6.4 teams create their own synthetic document packages |
| 🧑‍🏫 Mentors | Deloitte (Day 1 office hours only, Mon 17:00-19:00) and AWS solutions architects, any mentor from the main guide |


---


### ⭐ Partner challenge


#### ⭐ Automating back-office document controls · Komerční banka

> 🏦

Challenge by **Komerční banka**: from incoming documentation to an auditable result and exception management. Also fits Track 4. Full brief attached below.

**❓ Question:** Can an AI agent take over a diverse set of back-office documents, recognise their type, extract key data, verify completeness and consistency, and pass only the exceptions to a human, without losing the audit trail?

**🎯 Context:** back-office teams check documents by hand, compare data across supporting materials and chase missing or ambiguous information. Build a generally applicable solution that speeds up the check, makes it more consistent and produces a traceable control protocol. The AI output supports the decision; it is not an automatic final approval.

**🛠️ Expected prototype:**

* Accept a package of documents for one business case.
* Check the set is complete: about 5-7 different documents, always defined in the "Contract" document. Classify each document, then extract the pre-defined attributes for its type, with a confidence level.
* If something is missing or specific inconsistencies appear, automatically trigger a request to the client to supplement or correct.
* Sort results into passed checks, discrepancies, warnings and manual review, and generate a cited, auditable protocol with a recommended next step for the back-office worker.
**⚙️ Technical tasks:**

* **Ingestion and preprocessing:** load PDFs and images, OCR, keep the link to the original page.
* **Classification:** determine the document type. Bonus: split multi-document PDFs and handle shuffled pages.
* **Extraction:** structured attributes with source citation and confidence score.
* **Rules engine:** configurable checks for completeness, consistency and logical links.
* **Human in the loop:** confirm, edit, reject or send back for supplementation.
* **Audit trail:** input versions, applied rule or model, run timestamp, history of human interventions.
**🎬 Demo scenario:** a happy path (a complete set passes and a protocol is generated), an error path (a document is missing, or a key data item is missing or doesn't match), and the automatic resolution or human next steps.

**📊 Evaluated on:** accuracy of classification, extraction and checks; traceability of evidence and explainability; robustness to document quality and variants; real-world usability for the back office.

**🚧 Guardrails:** rules must be separate from extraction and easy to change; the rules should improve continuously from real decisions.

> 🧪

**No documents are provided.** KB does not share any documents for this challenge. Create your own **synthetic** document packages (a Contract that defines the 5-7 required documents, plus the supporting documents, incl. scans, missing pages and inconsistent data for the error path). No real client data.

**📄 Brief from KB:**

📎 **Attachment:** [KB_Challenge_Back-office_document_controls.docx](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/a79644a9-f30a-4e11-921e-d3ff515e4d96/KB_Challenge_Back-office_document_controls.docx?table=block&id=308c6e36-4f1f-4f63-866a-4bdd903a7170&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=muVFQa0aVCTBs-ZvlOabbSQQi-iOCR2WRcNqD-ysieo)  
📄 *Local Markdown Version:* [KB_Challenge_Back-office_document_controls.md](../attachments/KB_Challenge_Back-office_document_controls.md)


---


### 🧩 More challenges in this track


#### 💸 Invoice-to-cash on autopilot

**❓ Question:** Can an agent run the whole receivables loop: read incoming invoices, match payments, chase late payers with personalised (and polite) follow-ups, and forecast cash?

**🛠️ Build:** A multi-step agent over synthetic ERP data: extraction → matching → dunning sequence → cash-flow forecast dashboard.


#### 📈 The treasury copilot

**❓ Question:** A CFO asks: "What's our FX exposure if the koruna moves 5%, and what should we hedge this week?" Can AI answer with numbers, reasoning and a proposed action, not a paragraph of generalities?

**🛠️ Build:** A treasury assistant over synthetic multi-currency positions: exposure calculation, scenario simulation, hedge proposal with a cost estimate.


#### 🦖 Legacy migration, translated by AI

**❓ Question:** Banks run critical batch jobs in COBOL or PL/SQL that nobody dares to touch. Can gen AI document, test and translate a legacy workflow into a modern, auditable pipeline?

**🛠️ Build:** From a provided legacy code sample: documentation, unit tests that capture current behaviour, and a modern re-implementation that passes those tests.


---


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| ☁️ AWS team account | One account per team with Amazon Bedrock, AgentCore and Kiro covered in the Toolbox. USD 800 budget per team. See the AWS Participant Guide | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |
| 🗄️ Synthetic data | ERP and position data, legacy code sample, TSYS transactions | Tech onboarding, Mon 10:30 |


### 💡 Tips

* Numbers beat prose: the treasury copilot should calculate, not just talk.
* For legacy migration, the tests are the proof. Show them passing on old and new code.
