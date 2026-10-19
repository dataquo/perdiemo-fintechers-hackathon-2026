---
title: "EU financial firm licences and regulator warnings (Mostly Right Dataset)"
source_url: "https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings"
llms_txt_url: "https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings/llms.txt"
fetched_at: "2026-10-19T21:04:00Z"
category: "dataset"
format: "Parquet / JSON API / S3"
aws_s3_path: "s3://ai-hackathon-datasets-422928733782/MostlyRIght/"
---

# EU financial firm licences and regulator warnings

**Check whether a European financial firm is licensed, live on SEPA Instant, sanctioned or named in a regulator warning.** 

One table brings together official registers from across the EU: 
* **ESMA registers** of investment firms, fund managers, crowdfunding providers, trading venues and crypto-asset firms (MiCA CASPs)
* **ECB list** of banks, money market funds and central banks
* **EBA register** of payment and e-money institutions
* **Czech National Bank (ČNB)** lists of banks, payment institutions and intermediaries
* **EPC SEPA Instant (SCT Inst)** and **Verification of Payee (VoP)** participant registers
* **Regulator warnings & blacklists** from AMF, ESMA non-compliant CASPs, and others
* **EU financial sanctions** (entities only)

An open, machine-readable dataset published on Mostly Right as immutable Parquet versions, with a documented column schema, a JSON query API, and direct download. It is preloaded in your team AWS account under `s3://ai-hackathon-datasets-422928733782/MostlyRIght/`.

---

## ⚡ Facts & Access

| Attribute | Value |
| --- | --- |
| **Slug** | `eu-financial-firm-licences-and-regulator-warnings` |
| **Canonical Page** | [mostlyright.md/datasets/...](https://mostlyright.md/datasets/eu-financial-firm-licences-and-regulator-warnings) |
| **Publisher** | Mostly Right (`mostlyrightmd`) |
| **Formats** | Apache Parquet (download), JSON (query and sample) |
| **AWS S3 Bucket** | `s3://ai-hackathon-datasets-422928733782/MostlyRIght/` (`eu-central-1`) |
| **Metadata API** | `GET https://mostlyright.md/api/v2/public/datasets/eu-financial-firm-licences-and-regulator-warnings` |
| **MCP Server for Agents** | `https://mostlyright.md/api/mcp` (search, schema, and sample rows need no credentials) |
| **Best Used In** | Track 1 (Agentic payments & payee check), Track 4 (KYB/KYC verification), Track 5 (AML counterparty screening) |

---

## 🛠️ How to Use It

1. **Read Table Schema:** No account needed (`GET https://mostlyright.md/api/v2/public/tables/b0bc56bb-2e3b-4304-a46d-eb94ceaeed9f/schema`).
2. **Fetch Sample Rows:** First 500 rows free without an account (`GET https://mostlyright.md/api/v2/public/tables/b0bc56bb-2e3b-4304-a46d-eb94ceaeed9f/preview`).
3. **Query via JSON API:** `POST https://mostlyright.md/api/v2/public/tables/b0bc56bb-2e3b-4304-a46d-eb94ceaeed9f/query` with `x-api-key: mr_use_…`.
4. **Local Parquet in AWS:** Copy from `s3://ai-hackathon-datasets-422928733782/MostlyRIght/` directly into your pandas/polars dataframes.

---

## 📊 Table: `counterparty_records`

- **Table ID:** `b0bc56bb-2e3b-4304-a46d-eb94ceaeed9f`
- **Slug:** `counterparty-records`
- **Immutable Version:** `faf55752-1330-5c91-a429-e8919ebceff3`

### Columns (35)

| Column | Type | Description |
| --- | --- | --- |
| `record_id` | string | Stable hash of record type and source record key (row primary key). |
| `record_type` | string | Type of record: `licence`, `payment_scheme`, `warning`, or `sanction`. |
| `source_list` | string | Source list: `esma_registers`, `ecb_mfi_list`, `eba_payments_register`, `cnb_banks`, `esma_casps`, `epc_scheme_registers`, etc. |
| `authority` | string | Authority issuing register, warning, or sanction (e.g. ČNB, ESMA, ECB, AMF). |
| `authority_country` | string | ISO 2-letter country code (or `EU` for EU-wide bodies). |
| `name` | string | Entity, firm, or participant name (or domain name for web-only warnings). |
| `other_names` | string | Trading name or aliases separated by pipe `\|`. |
| `country` | string | ISO 2-letter country code of counterparty. |
| `national_id` | string | National ID: e.g. Czech IČO, ECB RIAD code, register number. |
| `lei` | string | Legal Entity Identifier (LEI) if available. |
| `bic` | string | 11-character SWIFT/BIC code for payment scheme participants. |
| `eu_reference_number` | string | EU reference number for sanctioned entities. |
| `un_id` | string | UN identifier for sanctioned entities. |
| `website` | string | Official website URL. |
| `website_domain` | string | Normalized domain (lowercase, no `www`). |
| `email_domain` | string | Domain of email address flagged in warnings. |
| `address` | string | Registered seat address. |
| `city` | string | Registered city. |
| `category` | string | Licence scope (credit institution, EMI, PI, MiCA CASP, fund manager, etc.). |
| `detail` | string | Permitted activities, services, branch head office, or exclusions. |
| `value_kind` | string | For warnings: website, email domain, name, or firm with details. |
| `passported_to` | string | Member states notified under cross-border freedom of services (pipe-separated). |
| `since` | date | Effective date: authorisation date, scheme readiness date, or warning date. |
| `until` | date | Expiration or revocation date if applicable. |
| `in_sct_inst` | boolean | Is participant live on SEPA Instant Credit Transfer (SCT Inst)? |
| `sct_inst_ready_since` | date | Date participant joined SCT Inst. |
| `sct_inst_leaving_date`| date | Date participant leaves SCT Inst. |
| `in_vop` | boolean | Is participant live on Verification of Payee (VoP)? |
| `vop_status` | string | Verification of Payee status as recorded by EPC. |
| `vop_role` | string | VoP capability: requesting checks, answering checks, or both. |
| `vop_ready_since` | date | Verification of Payee readiness date. |
| `vop_leaving_date` | date | Date leaving VoP. |
| `name_count` | integer | Number of distinct aliases on sanctions lists. |
| `regulation_url` | string | Official Journal EU act link for sanctioned entity. |
| `source_url` | string | Official notice, register entry, or regulatory alert URL. |

---

## 💡 Practical Hacks for Hackathon Teams

1. **Pre-Payment Verification (Track 1)**: Before an agent dispatches money, query `counterparty_records` by payee IBAN/BIC or website domain. Reject or flag transfers to unverified entities or entities on warning/sanction lists.
2. **KYB Enrichment (Track 4)**: Automatically cross-reference applicant merchant IČO, BIC, or domain name with regulatory status and SEPA VoP readiness.
3. **AML Risk Scoring (Track 5)**: Enrich transaction logs with counterparty licence type and jurisdiction risk ratings.
