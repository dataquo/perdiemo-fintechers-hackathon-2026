---
title: "Track 3 · Cybersecurity and fraud in the age of gen AI"
source_notion_id: "3fc1e819-9813-8137-8ffd-debbd69b66be"
source_url: "https://thefintechers.notion.site/3fc1e819981381378ffddebbd69b66be"
fetched_at: "2026-10-19T19:10:58.795Z"
category: "track"
---

# Track 3 · Cybersecurity and fraud in the age of gen AI

> 🛡️

**Attackers already use gen AI. Build the defence.** Deepfakes, AI-written scams and attacks on AI agents themselves.


### 🧭 At a glance


| 🤝 Partners | Mastercard, AWS |
| --- | --- |
| 🧑‍🏫 Mentors | AWS solutions architects and any mentor from the main guide. Looking for customer-facing fraud alerts on WhatsApp/SMS? That is Infobip's use case in Track 4 |
| ⚠️ Hard rule | Synthetic samples only. No cloning of real people's voice, face or identity |


---


### 🧩 Challenges


#### 🎙️ Deepfake-proof the call centre

**❓ Question:** A "customer" calls the bank with a cloned voice and asks to change the payout account. Can you detect the deepfake in real time and design the fallback verification flow?

**🛠️ Build:** Real-time voice or video deepfake detection plus a step-up verification UX that does not destroy the customer experience.

**✅ A strong solution shows:** detection quality on synthetic samples and a fallback flow that a real customer would accept.


#### ⚔️ The AI-vs-AI fraud duel

**❓ Question:** If fraudsters use LLMs to generate phishing, synthetic identities and scam scripts at scale, can a defending AI detect patterns that rule-based systems miss?

**🛠️ Build:** A sandboxed red-team generator (synthetic targets only) plus a blue-team detector; measure detection rates on transaction and communication data.

**✅ A strong solution shows:** measured detection rates, not just a demo of one caught scam.


#### 🔐 Securing the agentic bank

**❓ Question:** When a bank deploys internal AI agents with access to systems and data, how do you stop prompt injection, data exfiltration and privilege escalation?

**🛠️ Build:** A security layer for agentic workflows (input sanitisation, permission scoping, anomaly detection on agent actions) and a live attack demo it withstands.

**✅ A strong solution shows:** a live attack that fails, and logs that show why.


---


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| ☁️ AWS team account | One account per team with Amazon Bedrock. USD 800 budget per team. See the AWS Participant Guide | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |
| 🗄️ TSYS data | Anonymised transactional data, available in every track | Tech onboarding, Mon 10:30 |

