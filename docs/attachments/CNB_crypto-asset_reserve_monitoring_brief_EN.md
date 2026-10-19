---
title: "CNB_crypto-asset_reserve_monitoring_brief_EN"
original_file: "CNB_crypto-asset_reserve_monitoring_brief_EN.md"
source_track: "Track 2 · Stablecoins and new financial infrastructure"
fetched_at: "2026-10-19T19:10:57.779Z"
---

# Hackathon Challenge Brief: Crypto-Asset Reserve Monitoring (System for Monitoring Crypto-Asset Backing)

*Track 2 · Stablecoins and new financial infrastructure. Challenge by the Czech National Bank (ČNB). English translation of the ČNB original (Czech original attached on the Track 2 page).*

**1. Context and main goal of the challenge**

The goal of the challenge is to build a micro-prudential SupTech (Supervisory Technology) tool that reduces the time mismatch (frequency mismatch) between continuous movements of digital liabilities on the blockchain and periodic reporting of actual reserves. The system should give the issuer, its partners, its customers, or the issuer's supervisor an automated, continuously updated view of crypto-asset backing, flag a drop below a set threshold in time, and support issuer stability in line with the MiCA regulation.

The expected output is a working prototype that connects simulated on-chain and off-chain data, calculates the current backing ratio, records the time and origin of the data it uses, and displays the result on a clear dashboard. Teams will also document the solution architecture, the data model, the assumptions made, how the interfaces are secured, and how they verify the correctness of the calculations and alerts.

Solutions will be judged on: correctness and auditability of the backing calculation, the ability to handle input data arriving at different frequencies, the quality of risk identification and signalling, the security of the integration interfaces, the clarity of the dashboard, and whether the prototype can be extended from EMT to ART.

**2. Phase 1: EMT (E-money Tokens) - 1:1 liquidity check**

This phase covers stablecoins whose value is pegged to a single fiat currency (e.g. EUR, CZK, USD). The issuer is subject to extremely strict daily liquidity-monitoring requirements and must maintain 100% reserve backing.

**Technical tasks for teams:**

-   **On-chain liability aggregation:** build an integration layer that queries public blockchain-explorer APIs (e.g. Etherscan) at configurable intervals for the volume of tokens in circulation. Every fetch must record the source, the time the data was obtained, the network identifier, and whether the query succeeded, so the result's recency and completeness can be assessed.

-   **Identifier unification:** use the DTI (Digital Token Identifier) methodology, rather than ISIN codes, to precisely identify tokens across different DLT networks.

-   **Off-chain asset collection:** build a REST API endpoint that simulates secure receipt of current balance data from protected accounts at depositary commercial banks.

-   **Reconciliation engine:** design a database model and computation layer (for example PostgreSQL and Python) that links real-time on-chain data with periodic bank data. The output must distinguish the last-update time of each source, the calculated backing ratio, and whether that ratio is based on sufficiently current data.

-   **Crisis alerting:** build an executive dashboard with an automated trigger that raises an alarm if the calculated backing ratio falls below 1:1. The alert must show the value found, the calculation time, the recency of the inputs used, and the source of the deviation where it can be identified.

**3. Phase 2: ART (Asset-Referenced Tokens) - dynamic portfolio valuation**

This phase extends the system to crypto-assets whose value is stabilised by reference to a basket of assets, commodities, several fiat currencies, or other crypto-assets. The issued token itself must not show the features of a financial instrument under the Czech Capital Market Undertakings Act (ZPKT) - for example a security, a derivative, or an interest-bearing unit certificate. Reserve assets must therefore be assessed separately: the system should track their composition, valuation, liquidity and risk as a portfolio backing the issued tokens.

**Definition of valid reserve assets (for algorithmic monitoring):**

-   Highly liquid financial instruments: short-term government bonds (in line with money-market-fund, MMF, standards) with minimal credit and market risk.

-   Commodities: physically allocated precious metals (e.g. gold with demonstrable custody at a licensed depositary).

-   Diversified fiat assets: deposits in several stable currencies spread across different credit institutions, to minimise concentration risk.

-   Reference crypto-assets: other highly liquid crypto-assets (on-chain collateral) with a transparently traceable on-chain structure.

**Technical tasks for teams:**

-   **Granular data model:** extend the Phase 1 database with a hierarchy of asset sub-classes to store detailed attributes such as valuation method, interest rate, or maturity of bonds held.

-   **Oracle integration (price feeds):** connect the system to external data providers for current market prices (mark-to-market), so the tool can revalue the fluctuating value of held commodities and bonds in real time.

-   **Optional - capital requirement validation:** extend the control mechanism to calculate the issuer's own funds. The system must let users set and document the regulatory rule applied, and verify whether the issuer holds capital of at least EUR 350,000, or capital set as a percentage of reserve assets, per the MiCA regulation.

-   **Optional - asset quality scoring:** add regulatory labels to the dashboard that classify held assets by liquidity and risk. Each label must trace back to the input data and the rule used to assign it; for example, fiat deposits may be rated higher than corporate debt where that matches the set criteria.
