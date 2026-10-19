# Hackathon Challenge Brief: Regulatory Radar and Automated Gap Analysis
*Czech National Bank (ČNB) · English translation of the official Czech brief*

## 1. Context and main objective of the challenge

The goal of this challenge is to build an AI RegTech tool that continuously monitors the regulatory pipeline relevant to financial institutions, in particular in the areas of DORA, the AI Act, PSD3 and MiCA, across relevant sources such as EUR-Lex, the ČNB (Czech National Bank), the EBA and ESMA. The tool should identify new or amended regulatory requirements, capture their effective dates and legislative status, and convert them into a structured form that can be used to assess their impact on a financial institution's internal policies.

The expected output is a working prototype consisting of a monitoring agent and a policy-mapping engine that operates on a provided sample of internal policies. For each relevant change, the solution should identify the affected parts of the internal documentation, propose a prioritised gap analysis and, for each finding, state the citation of the regulatory source, an explanation of the link to the internal rule, a confidence level and a recommended next step.

Solutions will be evaluated on the completeness and accuracy of the regulatory monitoring, the quality of mapping requirements to internal policies, the correctness and traceability of citations, the ability to distinguish binding obligations from proposals and supervisory (methodological) expectations, the appropriateness of the prioritisation of identified gaps, robustness to ambiguous wording, and the clarity of the output report for compliance, risk and the owners of the affected processes.

## 2. Phase 1: Monitoring the regulatory pipeline

This phase focuses on the automated collection, normalisation and assessment of regulatory documents. The agent should track new acts, amendments, technical standards, guidelines, opinions, consultations, supervisory communications and ESA Q&As, distinguish their legal status and build a timeline of expected impacts.

**Technical tasks for competing teams:**

- **Source collection and deduplication:** Connect the agent to provided or publicly available outputs from EUR-Lex, the ČNB, the EBA and ESMA. The system must remove duplicates, keep the original document and record the source, publication date, version, language and retrieval time.
- **Classification of regulatory status:** Distinguish between a proposal, an adopted regulation, an amendment, an implementing or regulatory technical standard, guidelines, a Q&A, a consultation paper and a supervisory communication; take into account the date of application, transitional periods and any follow-up acts.
- **Change detection:** Compare new and previous versions of documents, extract added, amended and repealed obligations, and briefly explain their substantive impact without losing the link to the original provision.
- **Audit trail and citations:** For every statement, store an exact reference to the document, article, paragraph or other identifiable part of the source, and make it possible to trace back the text the agent relied on.
- **Regulatory radar:** Display an overview of changes by regulation, topic, status, expected effective date and urgency; allow filtering and alerts for new or significantly changed requirements.

## 3. Phase 2: Internal policy mapping and gap analysis

This phase extends the solution with a semantic comparison of regulatory requirements against a sample of a financial institution's internal policies, which competing teams source themselves. The engine should recognise whether a requirement is already covered, only partially covered, in conflict with an internal rule or not addressed at all, and compile findings that can serve as input for expert review.

**Technical tasks for competing teams:**

- **Policy ingestion and structuring:** Load the provided sample of internal policies, split it into logical units and preserve the identification of the document, chapter, owner, version and effective date, where this information is available.
- **Optional: connection to the institution's systems:** Through a secure, read-only connection with the least privileges necessary, search for and retrieve from the financial institution's document management system the internal policies that are substantively related to the identified regulatory change. The solution must record the source and retrieval time of each document and must not change its content. The solution must include an explainable mechanism for assessing document relevance that limits the inclusion of thematically unrelated policies; for example, a change in DORA requirements should not automatically lead to the selection of policies governing capital adequacy.
- **Requirement-to-policy mapping:** Link individual regulatory obligations to specific provisions of internal policies and show the reason for the mapping, citations on both sides and a confidence level. One requirement may be linked to several policies, and one policy to several obligations.
- **Gap classification:** Distinguish between full coverage, partial coverage, missing provision, conflict, outdated reference and an inconclusive result requiring human review. The agent must not present an unverified match as a legal conclusion.
- **Prioritisation:** Set priority based on how binding the requirement is and when it takes effect, the scope of affected processes, the potential regulatory or operational impact, the severity of the gap and the confidence level of the analysis. The rules used must be configurable and explainable.
- **Cited gap report:** Generate a prioritised report containing the regulatory requirement, the affected internal policy, the type and description of the gap, supporting citations, the recommended remediation, the proposed owner, the target date and the status of expert review and approval. Supported statuses must include at least: pending review, approved, approved with changes, rejected, and returned for completion.
- **Human-in-the-loop and approval workflow management:** The solution must allow an authorised expert to review, confirm, edit, reject or return each finding for completion, and to record the corresponding review and approval status, the reviewer's identity, the time of the decision and any justification. It must be possible to use the feedback in subsequent runs without overwriting the original audit trail and while keeping the history of status changes.
- **Optional: draft amendment text:** For selected gaps, prepare a draft amendment to the internal policy, clearly marked as a working draft, with a citation of the source and an explanation of which obligation the draft addresses.
