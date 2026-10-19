---
title: "Track 5 · Compliance and RegTech copilots"
source_notion_id: "3fc1e819-9813-8119-ae58-d48c1f2656a3"
source_url: "https://thefintechers.notion.site/3fc1e81998138119ae58d48c1f2656a3"
fetched_at: "2026-10-19T19:11:07.759Z"
category: "track"
---

# Track 5 · Compliance and RegTech copilots

> ⚖️

**Copilots that a regulator would sign off on.** Regulatory monitoring, AML transaction monitoring and AI Act audits, with challenges from the Czech National Bank and FINREG PARTNERS.

> 🔥

**Recommended in this track:** ⭐ **FINREG PARTNERS AML triage**: 🗂️ ČNB synthetic dataset (about 400,000 transactions), AML Crash Course, 🏆 **CZK 40,000 in legal services** · ⭐ **ČNB regulatory-change radar**: written by the regulator, masterclass, 🗂️ a real internal bank policy from Partners Banka to map against, and 🧑‍🏫 Jan Bridzik, who also sits on the jury · **Transaction monitoring copilot**: 🗂️ the same ČNB dataset and 🧑‍🏫 ČNB mentors.


### 🧭 At a glance


| 🤝 Partners | Czech National Bank (ČNB), FINREG PARTNERS, Partners Banka (internal policy for the regulatory-change radar), Deloitte |
| --- | --- |
| 🏆 Challenge prize | **FINREG PARTNERS awards CZK 40,000 in legal services** to the 1st-place team, if that team worked on the FINREG PARTNERS AML challenge |
| 🎓 Masterclass | **AML Crash Course** by FINREG PARTNERS, with ČNB experts answering questions. Useful for both AML challenges (FINREG PARTNERS triage and the transaction monitoring copilot). Mon 19 Oct 13:30-14:30, Masterclass room 1, 1st floor, 45-50 min incl. Q&A · **Regulatory-change radar masterclass** with Jan Bridzik (ČNB), Mon 19 Oct 13:30-14:30, Masterclass room 2, 1st floor **(TBC)!!!**. Mentors may add more masterclasses after team formation if they see interest; any new masterclass is announced on Circle |
| 🧑‍🏫 Mentors | Jan Bridzik (ČNB, Mon 13:00-14:30, Tue 07:30-09:00) · Jan Koník, Václav Tětek, Tereza Štichová (ČNB) · Oliver Zrno (FINREG PARTNERS, Mon 17:00-19:00, Tue 09:00-11:00) |


---


### ⭐ Partner challenges


#### ⭐ AML transaction monitoring: triage and red-flag escalation · FINREG PARTNERS

> 🔎

Challenge by **FINREG PARTNERS**, built on ČNB's synthetic data. **Updated 18 Oct:** the ruleset now uses July 2026 transactions vs. Q2 2026 client statistics. Prize: **CZK 40,000 in FINREG PARTNERS legal services** for the 1st-place team, if it worked on this challenge. Jan Šovar (FINREG PARTNERS) introduces it on stage at about 10:25.

**❓ Question:** AML transaction monitoring is only part of the puzzle. Every red flag has to be processed, analysed and escalated where necessary. Red flags heavily outnumber the capacity of AML staff, many are false positives, and the real ones have to reach the right person in time while keeping conflicts of interest at bay. Can an automated system save AML staff time, relay important flags to the right people and make every decision explainable, justified and auditable?

**🛠️ Build:** an automated system that (i) generates red flags using the ruleset below and (ii) sorts, rates and escalates each red flag to the right person. Convert all amounts to CZK. Client volume is the sum of all of a client's transactions regardless of direction (in/out), unless the briefing says otherwise.


#### 🚩 Red-flag ruleset


| Type | Rule | Alert unit |
| --- | --- | --- |
| 🅰️ **A · Client profile discrepancy** | Daily volume in July 2026 is greater than 25% of the projected monthly volume, or greater than 3x the average daily volume in Q2 2026; or a single transaction is greater than 2x the maximum transaction in Q2 2026. Clients inactive in Q2 2026 are compared to projected volumes only | One alert per client |
| 🅱️ **B · High-risk jurisdiction / PEP** | A transaction above CZK 10,000 where the payer, payee or client country is on the EU or FATF high-risk jurisdictions list; or an outgoing transaction of a Politically Exposed Person above CZK 100,000 (where direction is unclear, any transaction) | One alert per transaction |
| ©️ **C · Flow-through account** | Within 24 hours the client receives incoming payments above CZK 100,000 and within 6 hours sends out at least 80% of that amount to another account (not the payer's account). Include any further red flags you identify | One alert per client |


#### ⚙️ For every red flag, the system must

1. **Triage:** false positive or needs human review, with the specific basis (client profile, history, AML risk score, client type, relationship specifics). No red flag is decided without a decision log.
1. **Priority 0-100** from risk factors: AML risk score, PEP, country, amount or volume, conduct discrepancies, length of the client relationship, how the contract was concluded, multiple flags on the same client.
1. **Assign the person responsible** for the final decision (escalation matrix and conflict-of-interest rules are given at the briefing).
1. **Log the final decision.**
> 💡

**FINREG PARTNERS' tip:** use AI for decision-making and navigating the ruleset, not for analysing every row of data.


#### 📤 Mandatory output

A **CSV with one row per alert**: `alert_id`, `alert_type`, `client_id`, `transaction_id`, `triage (FP/REVIEW)`, `priority (0-100)`, `executive_role`, `executive_person`, `approver (4 eyes)`, `reason (text)`, `log`.

**Hand in with your repo:** code, the mandatory CSV, a demo (max 5 min for FINREG PARTNERS; the main stage pitch is 3 min plus 2 min jury Q&A) and a description of your decision logic backed by the data (max 2 pages), focused on points 1-4 above.


#### 📊 FINREG PARTNERS evaluation


| Criterion | Weight |
| --- | --- |
| Triage and priority correctness (sample of 30-45 alerts, 10-15 per type) | 40% |
| Correctness of escalation (vs. the escalation matrix and conflict-of-interest rules) | 20% |
| Decision justification (on a sample of alerts) | 25% |
| Audit log, demo and solution | 15% |

This scoring decides FINREG PARTNERS' challenge prize. The overall top 3 are still decided by the main jury criteria.

**📄 Brief from FINREG PARTNERS:**

📎 **Attachment:** [AML challenge.docx](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/3488aa02-9076-458e-a471-b70660d7c136/AML_challenge.docx?table=block&id=64617b0c-5cc7-4bde-9e09-0d1f383efe7e&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=2h340QGNbFmLGOKtcPbzMIq0wWfcdH1vMgdyI-WoSjY)  
📄 *Local Markdown Version:* [AML challenge.md](../attachments/AML challenge.md)

**📦 Data from ČNB:** a July 2026 payment transaction log and a client log with Q2 2026 statistics, in ČNB's synthetic version: about **400,000 payment transactions from about 5,500 clients**. Find it in the shared AWS bucket under `CNB/` (see the ‣). Two tables:

* **Transactions:** transaction ID, client ID, date, time, amount, currency, payer and payee country, anonymised payer and payee account, transaction type.
* **Clients:** client ID, country, contract date and channel, PEP flag, client type (natural person, natural person acting in a business capacity, legal person), projected CZK volume and number of transactions at contract conclusion, actual CZK volume, number and maximum transaction amount in Q2 2026, AML risk score, other statistics (e.g. MCC) where available.
> 📦

The ČNB dataset is handed out to registered teams at tech onboarding (Mon 10:30) and on Circle. Fully synthetic, no real clients.


---


#### 🔆 The regulatory-change radar · ČNB

> 📡

Challenge by the **Czech National Bank**, mentored by Jan Bridzik (Director of ICT Risk Control and AML/CFT Supervision). Full brief (English translation and Czech original) attached below. Jan Bridzik runs a regulatory-change radar masterclass on Monday 13:30-14:30 in Masterclass room 2, 1st floor (TBC).

**❓ Question:** Can an AI agent read the regulatory pipeline, map each change to a bank's internal policies and draft the gap analysis?

**🛠️ Build:** A working prototype with two parts. **Phase 1, monitoring agent:** tracks the regulatory pipeline across **DORA, the AI Act, PSD3 and MiCA**, drawing on EUR-Lex, ČNB, EBA and ESMA; deduplicates sources, classifies legal status (proposal, adopted act, amendment, RTS/ITS, guidelines, Q&A, consultation, supervisory communication), detects added, amended and repealed obligations, keeps an audit trail with exact citations and shows a filterable regulatory radar. **Phase 2, policy-mapping engine:** maps each obligation to specific provisions of a sample of internal policies, classifies gaps (full, partial, missing, conflict, outdated reference, inconclusive), prioritises them with configurable and explainable rules, and generates a cited gap report with recommended remediation, owner, target date and a human-in-the-loop approval workflow (pending review, approved, approved with changes, rejected, returned for completion). Optional: read-only connection to an institution's document system, and draft amendment text clearly marked as a working draft.

**✅ A strong solution shows:** every gap traced to a specific article and a specific policy clause, prioritised, with confidence and a reviewer step. ČNB evaluates completeness and accuracy of monitoring, quality of requirement-to-policy mapping, correct and traceable citations, distinguishing binding obligations from proposals and supervisory expectations, sensible prioritisation, robustness to ambiguous wording and a report that compliance, risk and process owners can understand.

**📄 Brief from ČNB:** 

📎 **Attachment:** [CNB_The_regulatory-change_radar_EN.docx](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/fd4d4279-b905-42d4-81f7-cb9a4c762206/CNB_The_regulatory-change_radar_EN.docx?table=block&id=3fd1e819-9813-80b0-b140-e77f6c4225ce&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=QnJFFl1T_3JDkcc4o0Cu9SR5zEWp9QkJaLCHtBFaxRQ)  
📄 *Local Markdown Version:* [CNB_The_regulatory-change_radar_EN.md](../attachments/CNB_The_regulatory-change_radar_EN.md)

📎 **Attachment:** [CNB_The_regulatory-change_radar_brief_EN.md](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/84aaa421-55c9-4983-ab76-d25cb7a3c2a5/CNB_The_regulatory-change_radar_brief_EN.md?table=block&id=90325818-66b6-4e9f-b15b-f2113c36e1ff&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=e0TV3E-j4mOJ-5S4cxYHlLb1aChfIs2njrIL910HgEY)  
📄 *Local Markdown Version:* [CNB_The_regulatory-change_radar_brief_EN.md](../attachments/CNB_The_regulatory-change_radar_brief_EN.md)

**📦 Policy set:** per the ČNB brief, teams source their own sample of internal policies (for example publicly available bank policies or ones you draft yourselves).

> 🏦

**New: a real internal policy from Partners Banka.** Partners Banka shared its internal regulation **B-055 Management of risks arising from the use of artificial intelligence** (owner: CRO, effective 16 July 2025, approved by the Board) as a starting policy set for the radar. It covers the bank's AI strategy, roles (AI Sponsor), third-party AI, internal AI use proposals, an AI tool register and AI-specific risks (bias, control over outputs, discrimination, documentability, AI Act and GDPR compliance, data leakage, model isolation). A natural first test: map AI Act obligations (and DORA ICT third-party rules) to its articles and show the gaps. English translation attached below; the Czech original is available from the organisers. Shared for hackathon use only, please do not redistribute. You can still add other policies of your own.

📎 **Attachment:** [PartnersBanka_B-055_AI_risk_management_policy_EN.md](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/99951c9f-fd89-42a9-ba82-63d43c499f50/PartnersBanka_B-055_AI_risk_management_policy_EN.md?table=block&id=4c26053f-6966-4b8e-af31-edeb5873083a&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=v_dH2lMp5WQg8vNR3rHU9W2OEed3zS5jA0Ry-Ej4v98)  
📄 *Local Markdown Version:* [PartnersBanka_B-055_AI_risk_management_policy_EN.md](../attachments/PartnersBanka_B-055_AI_risk_management_policy_EN.md)


---


### 🧩 More challenges in this track


#### 🔎 The transaction monitoring copilot

**❓ Question:** AML monitoring is hard because of the volume of data and the noise, not because the rules are unclear. Most flags are false positives. Can AI watch a realistic stream of transactions, flag only the ones that really need a human look, and explain each flag well enough that a compliance analyst (and later a regulator) would accept it?

**🛠️ Build:** A system that scores transactions against AML typologies, ranks them by risk and writes a clear, data-backed explanation for every flag. Stretch goals: sensitivity tuning for a compliance officer, or a case-narrative generator a reviewer could sign off.

**📦 Data:** the same ČNB synthetic dataset (about 400,000 transactions from about 5,500 clients), handed out at tech onboarding.

**🎓 Masterclass:** the AML Crash Course (Mon 13:30-14:30, Masterclass room 1) covers this challenge too.


#### 🤖 The AI Act self-audit

**❓ Question:** A bank has 40 AI models in production. Which are high-risk under the AI Act, and what documentation is missing? Can this audit run itself?

**🛠️ Build:** A model-inventory copilot that classifies AI systems by AI Act risk tier, generates the required technical documentation skeletons and flags gaps.


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| 🗂️ ČNB synthetic AML dataset | ~400,000 transactions, ~5,500 clients, PEP flag, AML risk, MCC codes | Tech onboarding, Mon 10:30 |
| 📄 Challenge briefs | ČNB radar brief and FINREG PARTNERS AML brief (attached above) | Download now |
| 🏦 Partners Banka internal policy | B-055 Management of risks arising from the use of AI (EN translation, attached above). Policy set for the regulatory-change radar | Download now |
| 📚 Regulatory sources | EUR-Lex, ČNB, EBA and ESMA, all public | Any time |
| ☁️ AWS team account | One account per team with Amazon Bedrock, USD 800 budget per team. See the AWS Participant Guide | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |


### 💡 Tips

* Go to the AML Crash Course on Monday at 13:30 if you take either AML challenge.
* Mentoring from ČNB is expert guidance, not a regulatory opinion or endorsement.

### 🇪🇺 Extra dataset: EU financial firm licences and regulator warnings

About 10,500 official public records (Mostly Right): regulator warnings (AMF blacklists, ESMA non-compliant CASPs), EU financial sanctions (entities only), ČNB and ESMA licence registers. Combine it with the ČNB synthetic AML dataset to screen counterparties for red flags. [Dataset page](https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings). Available in your team AWS account from tech onboarding on Day 1.

