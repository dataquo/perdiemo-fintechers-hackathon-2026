---
title: "AML challenge"
original_file: "AML challenge.docx"
source_track: "Track 5 · Compliance and RegTech copilots"
converted_at: "2026-10-19T19:11:05.263Z"
---

**AML challenge: ****Triage and red flag escalation**** - ****FINREG PARTNRES**

**Prize****: 40****.****000 ****CZK usable on our legal services**

**Question**

AML transaction monitoring is only a part of the puzzle. Every identified red flag has to be processed, analysed and escalated where necessary. The number of identified red flags heavily outnumbers the capacity of AML personnel � significant number of red flags are false positive flags, and the real flags have to be relayed to the right person in time while keeping conflicts of interests at bay. Can an automated system optimize valuable time of AML personnel, relay important flags to the right people and ensure that every decision is explainable, justified and auditable?

**Data**

* **Payment transaction log**** ****from**** ****July**** 2026**�(~ 400.000 transactions): transaction ID, client ID, date, time, volume, currency, payer country, payee country, anonymised payer and payee account number, transaction type.
* **Client log****:**�client ID, client country, date and form of contract conclusion, Politically Exposed Person (yes/no), client type (natural person / natural person acting in a business capacity / legal person), projected volume CZK and number of payment transactions at the time of contract conclusion, actual volume CZK, number and a maximum payment transaction amount from Q2 of 2026, AML risk-score; other statistical data (e. g. MCC), if available.
**Build**

Build an automated system, which (i) can generate red flags pursuant to the provided ruleset below; and (ii) can sort, rate and escalate each red flag to the right person.

Transaction volume shall be converted to CZK. Client volume reflects the sum of every transaction of a client regardless their direction (in/out) unless specified otherwise at the initial briefing.

Red flag identification ruleset:

* **Typ****e**** A � ****Discrepancy of client profile **(one alert per client): daily volume from July 2026 is greater 25 % than the projected monthly volume or is greater 3x than average daily volume from Q2 of 2026., or a single transaction is greater 2x than the max volume from Q2 2026. Inactive clients in Q2 of 2026 are only compared to projected volumes.
* **Typ****e**** B � ****Shady jurisdiction**** / PEP**�(one alert per transaction): one transaction greater than 10.000 CZK, where the country of payer, payee or a client is part of the EU or FATF high-risk jurisdictions list; or an outgoing transaction (where the direction is not clear, any transaction) of a client who is a Politically Exposed Person (PEP) is greater than 100.000 CZK.
* **Typ****e**** C � ****F****l****ow-through account **(one account per client): the client, during 24 hours, accepts incoming payment transactions greater than 100.000 CZK and in 6 hours executes outgoing payment transactions amounting to at least 80 % of the incoming payment transactions to another account (payment account other than a payment account of the payer). Should further red flags be identified, make sure they are included.
*For every red flag, the automated **system** shall*

* **Make a triage decision **� false positive / require human oversight and justify the decision by stating specific basis for such decision (client profile, client history, AML risk score, client type, client relationship specifics etc.). No reg flag shall be decided without proper decision log.
* **Assign priority**�(0�100) based on risk factors: AML risk score, PEP, country, amount / volume, client conduct discrepancies, duration of a relationship with the client, form of contract conclusion, conjunction of multiple flags of the same client.
* **Assign the person responsible for ultimately deciding on a red flag****.**
* **Log the final decision****.**
Recommendation: make use of AI for decision-making and ruleset navigation, not for analysing every row of data.

**Outcome**** (****mandatory**** form****at****)**CSV with a row for every alert:�alert_id, alert type, client_id, transaction_id, triaz (FP/REVIEW), priority (0�100), executive_role, executive_person, approver (4 eyes), reason (text), log.

**Evaluation criteria**

* **Triage and priority correctness**�� will be judged on a sample of 30�45 alerts (10�15 per type) (40 %).
* **Correctness of escalation**�� compared to the escalation matrix and conflicts of interest rules (20 %).
* **Decision justification**�� judged on a sample of alerts (25 %).
* **Audit log, demo and solution **(15 %).
**Expected data to provide along with your outcome**

Code, mandatory CSV, demo max. 5 minutes a description of decision logic supported by used data (max. 2 pages) focusing on the ruleset above (points 1-4).

