---
title: "Track 1 · Agentic payments and money movement"
source_notion_id: "3fc1e819-9813-8165-aa83-d4679ab20272"
source_url: "https://thefintechers.notion.site/3fc1e81998138165aa83d4679ab20272"
fetched_at: "2026-10-19T19:10:56.483Z"
category: "track"
---

# Track 1 · Agentic payments and money movement

> 💳

**AI agents that move, reconcile and protect money.** Build agents that run real merchant payment operations on a sandbox: reconciliation, natural-language payment ops and safe agentic checkout.

> 🔥

**Recommended in this track:** all three challenges run on ready-made data and tools. 🧪 MoroSystems payments sandbox API · 🗂️ TSYS transaction data · 🗂️ Mostly Right EU licences and warnings dataset for payee checks. Data is ready in your AWS account on Monday, so you can start building straight away.


### 🧭 At a glance


| 🤝 Partners | MoroSystems (payments sandbox), TSYS (transaction data), AWS and Deloitte |
| --- | --- |
| 🗄️ Data | TSYS sandbox transaction data + MoroSystems payments sandbox API, synthetic bank statements |
| 🧑‍🏫 Mentors | AWS solutions architects, any mentor from the main guide |
| 🎯 Good fit for | Payments engineers, agent builders, anyone who has fought with reconciliation spreadsheets |


---


### 🧩 Challenges


#### 🧾 The self-reconciling merchant

**❓ Question:** Can an AI agent reconcile a merchant's daily transactions (payouts, fees, refunds, chargebacks) without human intervention, and explain every match it makes?

**🛠️ Build:** An agent that ingests the TSYS sandbox dataset, reconciles it against simulated bank statements, flags exceptions and produces an auditable explanation log.

**✅ A strong solution shows:** every match explained, exceptions routed to a human with a reason, and an audit log a finance team could hand to an auditor.


#### 💬 Conversational payment operations

**❓ Question:** Can a merchant run payment operations ("why did this transaction fail?", "refund all orders from customer X", "what were my fees last month?") through natural language, safely?

**🛠️ Build:** A copilot over the TSYS data with guardrails: read vs. write actions, confirmation flows and an audit trail for every agent-initiated operation.

**✅ A strong solution shows:** the agent never executes a write action without confirmation, and every answer cites the transactions it is based on.


#### 🛒 Fraud-aware agentic checkout

**❓ Question:** When AI agents shop on behalf of humans, how does a merchant tell a legitimate buyer-agent from a fraud bot?

**🛠️ Build:** A prototype agent-to-merchant checkout protocol with intent verification, spending mandates and real-time risk scoring from sandbox transaction patterns.

**✅ A strong solution shows:** a clear mandate model (who authorised what, up to which limit) and a risk score you can explain.


---


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| ☁️ AWS team account | One account per team with Amazon Bedrock. USD 800 budget per team. See the AWS Participant Guide, so spend efficiently | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |
| 💳 MoroSystems sandbox | Payments sandbox API for Track 1 | Tech onboarding, Mon 10:30 |
| 🗄️ TSYS data | Anonymised transactional data, available in every track | Tech onboarding, Mon 10:30 |
| 🤖 Models | Any LLM or model; Bedrock recommended for credits | All event |


### 💡 Tips

* Start from the data: map payouts, fees and refunds first, then add the agent.
* Agents that move money need guardrails. Show your confirmation and audit design in the demo.
* Sandbox and synthetic data only. No real cards, accounts or PII.

### 🇪🇺 Extra dataset: EU financial firm licences and regulator warnings

About 10,500 official public records (Mostly Right): licences, SEPA Instant and Verification of Payee participants, regulator warnings and EU sanctions. Great for a fraud-aware agentic checkout: have your agent check the payee's licence, warnings and SCT Inst / VoP reachability before it moves money. [Dataset page](https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings). Available in your team AWS account from tech onboarding on Day 1.

