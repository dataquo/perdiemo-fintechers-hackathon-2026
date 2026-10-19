---
title: "Track 4 · Gen AI onboarding, KYC and trust"
source_notion_id: "3fc1e819-9813-81f3-97a3-f77d4d2a595f"
source_url: "https://thefintechers.notion.site/3fc1e819981381f397a3f77d4d2a595f"
fetched_at: "2026-10-19T19:11:03.680Z"
category: "track"
---

# Track 4 · Gen AI onboarding, KYC and trust

> 🪪

**Onboarding in minutes, with a defensible audit trail.** KYB, KYC, identity proofing and conversational onboarding, with two partner challenges from Apify and Tapaya.

> 🔥

**Recommended in this track:** three partner-backed challenges. ⭐ **Apify web footprint**: 🎁 USD 100 credits per person, 🧑‍🏫 four Apify mentors on site · ⭐ **Tapaya merchant KYB**: 🗂️ KYB training pack, masterclass Mon 14:30, 🧑‍🏫 Tapaya's CTO · ⭐ **Infobip onboarding and fraud prevention**: 🧪 Infobip account per team, masterclass Tue 09:00, 🧑‍🏫 Infobip mentor. Tip: combine Apify and Tapaya for the online-presence part of KYB.


### 🧭 At a glance


| 🤝 Partners | ⭐ Apify and ⭐ Tapaya (partner challenges), ⭐ Infobip (onboarding and fraud-prevention tooling), AWS |
| --- | --- |
| 🎁 Perks | Apify USD 100 credits per person · Infobip account per team (400 AI credits, 200 messages per channel, AgentOS) · Tapaya KYB training pack |
| 🧑‍🏫 Mentors | Apify: Petr Seidner, Dušan Vystrčil, Lukáš Průša, Matěj Jurčák (rotating, both days) · Tapaya: Petr Zahradník (Mon 10:00-13:00, Tue 09:00-11:00) · Infobip: Francesco Tonelli (Mon 17:00-19:00, Tue 10:00-12:00) |
| 🗄️ Registries | Czech and EU public registries (ARES, OR), sanctions and PEP lists |


---


### ⭐ Partner challenges


#### ⭐ Scoring small businesses by their web footprint · Apify

> 🌐

Partner challenge by **Apify**. Credits: USD 100 per person, [claim here](https://app.notion.com/p/3f7f39950a2280e69684e6fcc5008416) (first 150 people, expire one month after activation).

**❓ Question:** Small businesses often have a thin credit file but a rich public trail online. Can you turn a company's web footprint (its e-shop, customer reviews and social media) into an explainable score that a lender, payments provider or insurer could actually use?

**🛠️ Build:** A pipeline that collects public web data about a small business with Apify Actors (e-shop catalogue, pricing and stock activity, review platforms, social profiles), cross-checks it against registry data (ARES, OR), extracts signals such as activity, growth, sentiment and consistency, and outputs a score with plain-language reasoning and a source link for every signal.

**✅ A strong solution shows:** a score you can explain signal by signal, each with its source, and registry cross-checks that catch inconsistencies.

**🧰 Tools:** Apify platform and Actors, ARES/OR, Amazon Bedrock.

**⚠️ Guardrails:** public business data only, respect site terms of use, no profiling of the private individuals behind the business.


#### ⭐ Merchant KYB intake · Tapaya

> 📝

Partner challenge by **Tapaya**. Data pack attached below. Petr Zahradník (CTO) runs a short masterclass on Monday from 14:30 in Masterclass room 1, 1st floor.

**❓ Question:** How can we efficiently extract and verify merchant business information for KYB with a mix of AI and human review?

**🛠️ Build:** A smart form or chatbot that extracts high-quality information from the business owner (company structure, business model, products sold, physical and online presence, documents), enriches it with EU public registries (ARES, PEP, sanctions lists) and prepares the output for KYB and AML checks, in structured and unstructured form.

**✅ A strong solution shows:**

* The intake catches weak or contradictory answers in the moment and asks the right follow-up question.
* Registry enrichment fills or cross-checks fields instead of asking the merchant again.
* A clear split between what AI decides and what goes to a human reviewer, with reasons.
* KYB/AML-ready output: structured fields with confidence scores plus a readable case summary.
**💡 Combine it:** use the Apify web-footprint challenge for the online-presence part.

**📦 Data from Tapaya:** anonymised merchant onboarding forms, including two filled examples showing what merchants actually submit (incomplete, inconsistent or nonsense answers included).

📎 **Attachment:** [Tapaya_merchant-kyb-training-pack.zip](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/0356a5e6-83bd-4062-b475-0b7bab40c2fd/Tapaya_merchant-kyb-training-pack.zip?table=block&id=f546704d-5970-4abf-9ada-9fe714b0ac46&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=FLhf2KAP8F6SA1kfECfuqu0itb8Ggd3EvUDU4FLgLZA)  
📄 *Local Markdown Version:* [Tapaya_merchant-kyb-training-pack.md](../attachments/Tapaya_merchant-kyb-training-pack.md)


---


### 🧩 More challenges in this track


#### ⏱️ KYB in ten minutes

**❓ Question:** Business onboarding takes days to weeks (registry checks, UBO discovery, document review). Can gen AI compress it to minutes while keeping a defensible audit trail?

**🛠️ Build:** A pipeline over Czech and EU public registries (OR/ARES, sanctions lists) plus document extraction, producing a structured KYB file with confidence scores and a human-review queue.


#### 🗣️ The explainable rejection

**❓ Question:** When AI declines an onboarding application, the customer and the regulator deserve to know why. Can every rejection be explained in plain language, in Czech and English?

**🛠️ Build:** An onboarding decision engine + a customer-facing explanation generator + an internal compliance justification, tested on synthetic edge cases.


#### 🧬 Trust score for the deepfake era

**❓ Question:** Selfie + ID checks are breaking under generative attacks. What replaces them?

**🛠️ Build:** Multi-signal identity verification (liveness, behavioural signals, document forensics, mobile-identity signals via Infobip APIs) with a measurable attack-resistance benchmark on a synthetic attack set.


#### 📱 Conversational onboarding on any channel

**❓ Question:** Can a customer open an account entirely through a conversation on WhatsApp, RCS or voice, with gen AI guiding, verifying and documenting every step?

**🛠️ Build:** An omnichannel onboarding flow on Infobip's communication and verification APIs: conversational KYC dialogue, silent mobile verification or OTP step-up, and a compliant audit log of the whole conversation.


---


### ⭐ Infobip use cases (Track 4 only)

> 💬

**Built on Infobip AgentOS**, an AI orchestration layer across WhatsApp, RCS, SMS, voice, push and other OTT channels: configurable AI agents and Knowledge Agents, tools and MCP-enabled services, sub-agents and agent-to-agent collaboration, LLM-agnostic, with hand-off to an AI-powered cloud contact centre when a human is needed. Infobip mentors **Track 4 teams only**, on the two directions below. Full guide attached at the end of this section.


#### 📲 Infobip 1 · Digital onboarding and activation

**🌍 Market scenario:** Czech banks have some of Europe's best digital banking and 85% of Czechs bank online (EU average 70%), but most customers use a fraction of their app. People open it about 150 times a year, yet the top weekly actions are checking the balance (45%) and sending money (31%). 72% say personalisation affects which bank they choose, but only 3% use the personalised tools their bank already offers, and 53% don't know the interest rate on their own savings. Banks keep shipping features (spending insights, card controls, savings goals, Bank iD services, new products) that customers never find.

**🛠️ Build:** meet customers where they already are (WhatsApp, Viber, RCS) with a short, relevant conversation that explains a feature, answers questions from the bank's approved content and guides the customer back into the app at exactly the right step. Run it across channels from one place: a message unopened in one channel follows up automatically in another.


#### 🚨 Infobip 2 · Customer-focused fraud prevention

**🌍 Market scenario:** Czech banks blocked a record CZK 12.2bn of attempted fraud in 2025 (over 85% of attempts), yet client losses rose by more than CZK 700m to CZK 2.13bn, then jumped another 79% in January-July 2026. 24% of Europeans have been tricked into transferring money, paying for fake goods or giving away data, and 56% never reported it. The risk peaks when stolen card details are used outside the EU, where strong customer authentication doesn't fully apply, and under PSD3/PSR banks will carry more of the loss.

**🛠️ Build:** connect the fraud engine to the customer in real time: an instant alert on the channel they actually read, automatic SMS backup, one-tap "yes, that was me" or "no, block it", and a hand-off to a human specialist with the full case when the customer is distressed.


#### 🔑 Infobip access and credits

* **One Infobip account per team**, one user (username + password, verified by 2FA at the start of the hackathon). Extra users on request during the event (phone number + email, verified by 2FA).
* **400 AI credits** per team account.
* **200 free-trial messages per channel** used: SMS, WhatsApp, RCS.
* **AgentOS, full access:** Journey, Agents, Automation Studio and Inbox with one human-agent operator licence per team.
* Credits and message allowances can be increased on request. Sandbox and synthetic data only, no production systems, no real customer data.
* **Mentor:** Francesco Tonelli, Principal Solution Engineer. Office hours Mon 17:00-19:00 and Tue 10:00-12:00. Infobip masterclass (conversational onboarding and fraud prevention) Tue 09:00-09:45, Masterclass room 1, 1st floor.
**📄 Infobip Guide for Hackers:**

📎 **Attachment:** [Infobip_Guide_for_Hackers.docx](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/1207593c-9546-4890-b733-df3870f1034b/Infobip_Guide_for_Hackers.docx?table=block&id=232e8038-5eb9-40c5-82da-7009f4c96333&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=4BMN7lMoQsuAdEMlEDYWdry9dZzKT4ulR_ZuABHKq1A)  
📄 *Local Markdown Version:* [Infobip_Guide_for_Hackers.md](../attachments/Infobip_Guide_for_Hackers.md)


---


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| 🎁 Apify | USD 100 credits per person, Apify Actors for web data. [Claim here](https://app.notion.com/p/3f7f39950a2280e69684e6fcc5008416) | Claim now |
| 💬 Infobip | One account per team: 400 AI credits, 200 free messages per channel (SMS, WhatsApp, RCS), AgentOS (Journey, Agents, Automation Studio, Inbox) with one human-agent operator licence. More on request | Access via the Infobip guide on Circle; masterclass Tue 09:00-09:45, Masterclass room 1, 1st floor |
| 📦 Tapaya KYB pack | Anonymised onboarding forms incl. two filled examples (attached above) | Download now |
| ☁️ AWS team account | One account per team with Amazon Bedrock. USD 800 budget per team. See the AWS Participant Guide | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |
| 🗄️ Registries | ARES and OR (Czech business registers), EU sanctions and PEP lists, all public | Any time |


### 💡 Tips

* Keep a human in the loop and show the hand-off in your demo. Judges score explainability.
* No real personal data. Use the Tapaya forms and synthetic profiles.

### 🇪🇺 Extra dataset: EU financial firm licences and regulator warnings

About 10,500 official public records (Mostly Right): ČNB licences and intermediaries, ESMA MiCA registers, EPC SEPA Instant / Verification of Payee participants, AMF and ESMA warnings and EU sanctions (entities only). Useful for KYB checks and trust scores: is this firm licensed, flagged or sanctioned? [Dataset page](https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings). Available in your team AWS account from tech onboarding on Day 1. Note: a firm missing from the table is not proof it is licensed or safe.

