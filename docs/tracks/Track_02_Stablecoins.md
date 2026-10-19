---
title: "Track 2 · Stablecoins and new financial infrastructure"
source_notion_id: "3fc1e819-9813-814b-be9d-ec17bc7e6022"
source_url: "https://thefintechers.notion.site/3fc1e8199813814bbe9dec17bc7e6022"
fetched_at: "2026-10-19T19:10:58.574Z"
category: "track"
---

# Track 2 · Stablecoins and new financial infrastructure

> 🪙

**Programmable money meets AI agents.** Build on-chain payment flows, agent-to-agent settlement and bank-grade tokenized money, with compliance built in.

> 🔥

**Recommended in this track:** ⭐ **Crypto-asset reserve monitoring**, a partner challenge written by the Czech National Bank (ČNB), the supervisor itself, on MiCA stablecoin backing. Brief attached below. Every challenge here is backed. 🎁 Free Tatum credits (one API across chains incl. Solana) · 🧪 Solana MCP for your coding agents (setup guide below) · 🧑‍🏫 mentors from Tatum, Solana CZE/SK and Marinade Finance. Claim the credits and set up the MCP before Monday.


### 🧭 At a glance


| 🤝 Partners | ⭐ Czech National Bank (ČNB, crypto-asset reserve monitoring partner challenge), Tatum (blockchain infrastructure), Solana CZE/SK community, AWS |
| --- | --- |
| 🎁 Perks | Free Tatum credits: one API across many blockchains incl. Solana (RPC, wallets, webhooks). [Claim them here](https://tatum.io/hackathon/fintechers) |
| 🧑‍🏫 Mentors | Filip Šipoš and Filip Kaštovský (Tatum engineers, help across all tracks), Milan Jandik (Solana CZE/SK), Michael Repetný (Marinade Finance), AWS solutions architects · ČNB experts for the crypto-asset reserve monitoring challenge (regulatory and supervisory questions) |
| ⛓️ Networks | Testnets only. No real funds |


---


### ⭐ Partner challenge


#### ⭐ Crypto-asset reserve monitoring · ČNB

> 🏛️

Partner challenge by the **Czech National Bank (ČNB)**: "Crypto-asset reserve monitoring: a system for monitoring crypto-asset backing". Full brief attached below, in English and the Czech original. Fits Track 2 tooling: Tatum for on-chain data, Solana for a fast reference chain and price feeds.

**❓ Question:** Stablecoin liabilities move on-chain every second, but reserves are reported periodically. Can you build a SupTech tool that gives the issuer, its partners, its customers or its supervisor a continuously updated view of crypto-asset backing under MiCA, and flags a drop below the threshold in time?

**🛠️ Build:** A working prototype that connects simulated on-chain and off-chain data, calculates the current backing ratio, records the time and origin of every input, and shows the result on a clear dashboard. Document the architecture, data model, assumptions, interface security and how you verify the calculations and alerts.

**Phase 1 · EMT (e-money tokens), 1:1 liquidity check:**

* **On-chain liability aggregation:** query blockchain explorer or node APIs at configurable intervals for tokens in circulation; log source, time, network ID and query success for every fetch.
* **Identifier unification:** identify tokens across DLT networks with the DTI (Digital Token Identifier), not ISIN.
* **Off-chain assets:** a REST endpoint that simulates secure receipt of balances from protected accounts at depositary banks.
* **Reconciliation engine:** a data model and computation layer (e.g. PostgreSQL and Python) linking real-time on-chain data with periodic bank data; show each source's last update, the backing ratio and whether the data is current enough.
* **Crisis alerting:** an executive dashboard that raises an alarm below 1:1, showing the value, calculation time, input recency and source of the deviation.
**Phase 2 · ART (asset-referenced tokens), dynamic portfolio valuation:**

* **Reserve assets:** short-term government bonds (MMF standards), physically allocated precious metals, fiat deposits in several currencies across several banks, and highly liquid on-chain crypto collateral.
* **Granular data model:** asset sub-classes with valuation method, interest rate and maturity.
* **Oracle integration:** market price feeds (mark-to-market) to revalue commodities and bonds in real time.
* **Optional:** own-funds check (at least EUR 350,000, or a percentage of reserve assets, per MiCA, with the rule documented) and asset quality labels traceable to inputs and rules.
**✅ A strong solution shows:** a correct, auditable backing calculation; sensible handling of inputs arriving at different frequencies; good risk signalling; secure integration interfaces; a dashboard a supervisor understands at a glance; and a clear path from EMT to ART.

**🧰 Suggested tools:** Tatum (one API across chains, so on-chain aggregation is a single integration; free credits), Solana devnet and Pyth price feeds for the oracle part, Etherscan or other explorers, Amazon Bedrock. Testnets and simulated balances only.

**📦 Data:** no dataset is handed out. Teams simulate the on-chain supply and the bank balances themselves, as the brief asks.

**📄 Brief from ČNB:**

📎 **Attachment:** [CNB_crypto-asset_reserve_monitoring_brief_EN.md](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/e73aa1ce-8c07-4a88-8a56-54fbd827f8be/CNB_crypto-asset_reserve_monitoring_brief_EN.md?table=block&id=caa721ba-fb23-48d3-a600-9769258a1247&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=H_QDDpvhQG8sc9CTVpJGRHnWiS36Lm73ZCgpbSTzJ6w)  
📄 *Local Markdown Version:* [CNB_crypto-asset_reserve_monitoring_brief_EN.md](../attachments/CNB_crypto-asset_reserve_monitoring_brief_EN.md)

📎 **Attachment:** [CNB_crypto-asset_reserve_monitoring_zadani_CZ.md](https://file.notion.so/f/f/a491e819-9813-8179-88b9-000321a52178/9c887170-549c-46cf-b718-c9e6c8e7b956/CNB_crypto-asset_reserve_monitoring_zadani_CZ.md?table=block&id=9dbaf499-653a-44e4-8764-11ec75c22815&spaceId=a491e819-9813-8179-88b9-000321a52178&expirationTimestamp=1792461600000&signature=4L358swvMf4nYft9DLwP_EsqOAwLxp8hml0DDngw-dU)  
📄 *Local Markdown Version:* [CNB_crypto-asset_reserve_monitoring_zadani_CZ.md](../attachments/CNB_crypto-asset_reserve_monitoring_zadani_CZ.md)


---


### 🧩 Challenges


#### 💶 The EUR stablecoin payroll rail

**❓ Question:** Can a CEE company pay international contractors in a MiCA-compliant EUR stablecoin, cheaper and faster than SEPA/SWIFT, with automatic tax and reporting artefacts?

**🛠️ Build:** Invoice → compliance checks → stablecoin payout on a testnet → accounting and reporting output. Compare cost and speed with traditional rails.

**✅ A strong solution shows:** the full flow end to end, a cost/speed comparison and the compliance checks made before every payout.


#### 🤖 Agents that pay each other

**❓ Question:** What does B2B commerce look like when AI agents negotiate and settle on-chain? How do you enforce spending limits, disputes and refunds between non-humans?

**🛠️ Build:** Two or more autonomous agents transacting in stablecoins on a testnet with programmable mandates (budget caps, escrow, dispute resolution).

**✅ A strong solution shows:** mandates that actually stop an agent from overspending, and a dispute path a human can follow.


#### 🏦 Tokenized deposits vs. stablecoins: the bank's answer

**❓ Question:** How could a bank offer instant 24/7 programmable money without losing deposits to stablecoin issuers?

**🛠️ Build:** A tokenized-deposit service prototype (testnet) with a gen AI compliance layer that screens transfers against AML and MiCA rules in real time.

**✅ A strong solution shows:** real-time screening with an explanation for every blocked transfer.


---


### 🛠️ Tech stack and data


| Resource | What you get | When |
| --- | --- | --- |
| ⛓️ Tatum | Free credits and tooling: one API across chains, RPC nodes, wallets, webhooks. [tatum.io/hackathon/fintechers](https://tatum.io/hackathon/fintechers) | Claim now |
| ☁️ AWS team account | One account per team with Amazon Bedrock, USD 800 budget per team. See the AWS Participant Guide | Logins at the AWS Toolbox, Mon 12:00-13:30 (mandatory) |
| 🗄️ TSYS data | Anonymised transactional data, available in every track | Tech onboarding, Mon 10:30 |


### 🤖 Solana MCP for your coding agents (guide by Solana CZE/SK)

Connect your coding agent (Codex, Claude Code, Cursor, VS Code, Windsurf) to the official Solana MCP. It gives the agent **current Solana docs** and a **checker for Anchor and Pinocchio program code**. No API key. It does not do wallets, signing or deploys. Mentor: Milan Jandik (Solana CZE/SK). The full PDF guide (10 pages, incl. the `check_solana.sh` script) is shared on Circle.


| Setting | Value |
| --- | --- |
| URL | `https://mcp.solana.com/mcp` |
| Transport | Streamable HTTP |


#### 1. Connect

* **Claude Code:** `claude mcp add --transport http solana-mcp https://mcp.solana.com/mcp` (add `--scope project` to share it with the team via `.mcp.json`)
* **Codex:** `codex mcp add solana-mcp --url https://mcp.solana.com/mcp`, then `codex mcp list`
* **Cursor:** in `.cursor/mcp.json` add `{"mcpServers": {"solana-mcp": {"url": "https://mcp.solana.com/mcp"}}}`
* **VS Code (Copilot agent mode):** in `.vscode/mcp.json` add `{"servers": {"solana-mcp": {"type": "http", "url": "https://mcp.solana.com/mcp"}}}`, or run *MCP: Add Server* and choose HTTP
* **Windsurf:** in Cascade MCP settings add the server under `mcpServers` with the URL in `serverUrl`
**Check it works:** start a new agent session and ask it to list the Solana MCP tools. You should see `program_autofixer`, `Solana_Documentation_Search`, `Solana_Expert__Ask_For_Help`, `list_sections` and `get_documentation` (some clients add a prefix).


#### 2. Set up your agents

Put project rules in your agent's instruction file (`CLAUDE.md`, `AGENTS.md` for Codex, `.cursor/rules/solana.mdc` for Cursor). Key rules from the guide:

* For anything Solana, use the Solana MCP tools before answering from memory (`list_sections` first, then `get_documentation`).
* After writing or changing program Rust, run `program_autofixer`, fix critical and high issues, and repeat until `require_another_tool_call_after_fixing` is false.
* Never ask for or use private keys, seed phrases or production credentials. Don't deploy or sign anything: a human does that.
* Running several agents? One agent per folder ("your lane"), every task self-contained, and "done" only with proof (command + output, test, commit).

#### 3. Check your program yourself too

The checker finds mechanical problems (e.g. unchecked math) but **not missing access control**. On every instruction that moves value or changes state, check: signers (or `has_one = authority`), account ownership (`Account<'info, T>`, every `UncheckedAccount` has a real `/// CHECK:`), PDA seeds and bump match the client, a wrong-signer test that fails, and token transfers with checked mint, token program, owner and checked math.


#### 4. If the tools don't show up

Use `check_solana.sh` from the PDF (attached inside it) to call the server directly: `./check_solana.sh --list` or `./check_solana.sh $(find programs -name '*.rs')`. Needs bash, curl and node. Exit code 0 = no critical/high issues, 1 = issues found, 2 = check didn't complete (treat as failed).


### 💡 Tips

* Claim Tatum credits before Monday so you don't lose hacking time.
* Show where MiCA matters in your flow (issuer, reserves, AML checks). Judges score regulatory awareness.
* Taking crypto-asset reserve monitoring? Start with Phase 1 (EMT) end to end, then extend to ART. Correct, auditable backing calculation is the first thing ČNB evaluates.
