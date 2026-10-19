# Hackathon Documentation & Reference Index

> **The FinTechers Hackathon 2026** — Prague (19–20 October 2026)  
> This directory stores structured Markdown exports of all hackathon tracks, infrastructure guides, partner challenges, and reference datasets for developers, AI coding agents (Antigravity, Cursor, Kiro, Claude Code), and human reviewers.

---

## 🧭 Navigation Map

### 1. Tracks & Partner Challenges (`docs/tracks/`)

| Track | Focus | Key Partners | Challenges & Materials | Markdown Document |
| :--- | :--- | :--- | :--- | :--- |
| **Track 1** | **Agentic Payments & Money Movement** | MoroSystems, TSYS, AWS, Deloitte | • The self-reconciling merchant<br>• Conversational payment operations<br>• Fraud-aware agentic checkout<br>• *Data:* MoroSystems sandbox API, TSYS data | [Track_01_Agentic_Payments.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_01_Agentic_Payments.md) |
| **Track 2** | **Stablecoins & New Financial Infrastructure** | Czech National Bank (ČNB), Tatum, Solana CZE/SK, Marinade Finance | • ⭐ **Crypto-asset reserve monitoring (ČNB challenge)**<br>• EUR stablecoin payroll rail<br>• Agents that pay each other<br>• Tokenized deposits<br>• *Tooling:* Solana MCP, Tatum credits | [Track_02_Stablecoins.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_02_Stablecoins.md) |
| **Track 3** | **Cybersecurity & Fraud in the Gen AI Era** | Mastercard, AWS | • 🎙️ Deepfake-proof the call centre<br>• ⚔️ The AI-vs-AI fraud duel<br>• 🔐 Securing the agentic bank (prompt injection & privilege escalation defence) | [Track_03_Cybersecurity_Fraud.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_03_Cybersecurity_Fraud.md) |
| **Track 4** | **Gen AI Onboarding, KYC & Trust** | Apify, Tapaya, Infobip, AWS | • ⭐ **Scoring small businesses by web footprint (Apify)**<br>• ⭐ **Merchant KYB intake (Tapaya)**<br>• ⭐ **Digital onboarding & fraud alerts (Infobip)**<br>• KYB in 10 minutes & explainable rejection | [Track_04_Onboarding_KYC_Trust.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_04_Onboarding_KYC_Trust.md) |
| **Track 5** | **Compliance & RegTech Copilots** | ČNB, FINREG PARTNERS, Partners Banka | • ⭐ **AML transaction monitoring triage (FINREG, CZK 40k prize)**<br>• ⭐ **Regulatory-change radar (ČNB)**<br>• Transaction monitoring copilot<br>• AI Act self-audit | [Track_05_Compliance_RegTech.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_05_Compliance_RegTech.md) |
| **Track 6** | **Finance Operations & Back-Office AI** | Komerční banka (KB), Deloitte, AWS | • ⭐ **Automating back-office document controls (KB challenge)**<br>• Invoice-to-cash on autopilot<br>• The treasury copilot<br>• Legacy migration | [Track_06_Finance_Ops.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/tracks/Track_06_Finance_Ops.md) |

---

### 2. Infrastructure & Environment Guides (`docs/guides/` & `docs/notion_guides/`)

- [**AWS Participant Guide**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/guides/AWS_Participant_Guide.md):
  - **Account Setup:** Single AWS account per team, USD 800 budget.
  - **Region:** Build strictly in `eu-central-1` (Frankfurt). SSO login lives in `eu-north-1`.
  - **Models:** Bedrock Claude models require `eu.` prefix (e.g. `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`). Claude 5 is blocked.
  - **Shared Datasets S3:** `s3://ai-hackathon-datasets-422928733782/` (read-only; copy locally).
  - **Cost Traps:** Avoid OpenSearch Serverless (~$23/day); use provisioned `t3.small.search` (~$1/day).
- [**Full Hackers Guide**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/notion_guides/Hackers_Guide.md): Complete guide with master agenda, rules, jury scoring criteria, venue logistics, and full team list.
- [**Developer & Agent Guide**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/DEVELOPER_AND_AGENT_GUIDE.md): Internal architectural decisions (ADR), model strategies, and statutory compliance rules (§§ 151–189 ZP).

---

### 3. Shared Reference Datasets (`docs/datasets/`)

- [**EU Financial Firm Licences & Regulator Warnings (Mostly Right)**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/datasets/EU_Financial_Firm_Licences_MostlyRight.md):
  - **Content:** 35 columns of unified EU registers (ESMA, ECB, EBA, ČNB), SEPA Instant (SCT Inst) and Verification of Payee (VoP) participation, regulator warnings/blacklists (AMF, ESMA), and EU sanctions.
  - **Availability:** In AWS S3 at `s3://ai-hackathon-datasets-422928733782/MostlyRIght/` and via MCP at `https://mostlyright.md/api/mcp`.
  - **Use Cases:** Counterparty payee verification before moving funds (Track 1), KYB enrichment (Track 4), and AML screening (Track 5).

---

### 4. Converted Documents & Challenge Briefs (`docs/attachments/`)

All original `.docx`, `.pdf`, and `.md` attachments from the official Notion track pages have been converted to native Markdown files:

#### 🏦 Track 6 · Komerční banka Challenge
- [**KB_Challenge_Back-office_document_controls.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/KB_Challenge_Back-office_document_controls.md): Official KB brief in Czech covering context, expected 5–7 document bundle, rules engine, HITL workflow, and evaluation. *(Converted from DOCX)*

#### ⚖️ Track 5 · Compliance & RegTech
- [**AML challenge.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/AML%20challenge.md): FINREG PARTNERS AML transaction monitoring triage challenge brief, red-flag ruleset, and scoring. *(Converted from DOCX)*
- [**CNB_The_regulatory-change_radar_EN.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/CNB_The_regulatory-change_radar_EN.md): Czech National Bank official brief for the regulatory pipeline radar & policy-mapping engine. *(Converted from DOCX)*
- [**CNB_The_regulatory-change_radar_brief_EN.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/CNB_The_regulatory-change_radar_brief_EN.md): ČNB radar brief markdown copy.
- [**PartnersBanka_B-055_AI_risk_management_policy_EN.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/PartnersBanka_B-055_AI_risk_management_policy_EN.md): Real internal AI risk management regulation (B-055) from Partners Banka (effective July 2025).

#### 🪪 Track 4 · Onboarding, KYC & Trust
- [**Infobip_Guide_for_Hackers.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/Infobip_Guide_for_Hackers.md): Complete hacker guide for Infobip AgentOS, omnichannel APIs, and 2FA fraud detection. *(Converted from DOCX)*
- [**Tapaya_merchant-kyb-training-pack.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/Tapaya_merchant-kyb-training-pack.md): Overview and contents of the merchant onboarding pack.
- **Extracted Form PDFs (`docs/attachments/tapaya_merchant_kyb/`):**
  - [Cedric-Incomplete-UBO-Declaration.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Cedric-Incomplete-UBO-Declaration.md)
  - [Merchant-Agreement-Short-Form.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Merchant-Agreement-Short-Form.md)
  - [Merchant-Application-Form-A.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Merchant-Application-Form-A.md)
  - [Merchant-Application-Form-B.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Merchant-Application-Form-B.md)
  - [Michal-Incomplete-Partner-Application.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Michal-Incomplete-Partner-Application.md)
  - [Partner-Application-Form.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Partner-Application-Form.md)
  - [Required-Documents-Checklist.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/Required-Documents-Checklist.md)
  - [UBO-Declaration-Form.md](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/tapaya_merchant_kyb/UBO-Declaration-Form.md)

#### 🪙 Track 2 · Stablecoins & ČNB Reserve Monitoring
- [**CNB_crypto-asset_reserve_monitoring_brief_EN.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/CNB_crypto-asset_reserve_monitoring_brief_EN.md): English brief for ČNB MiCA EMT/ART reserve monitoring.
- [**CNB_crypto-asset_reserve_monitoring_zadani_CZ.md**](file:///d:/_DOCUMENTS/_SCRIPTS/PERDIEMO-FTH/docs/attachments/CNB_crypto-asset_reserve_monitoring_zadani_CZ.md): Czech original zadání from ČNB.
