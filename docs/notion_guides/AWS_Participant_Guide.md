---
title: "AWS Participant Guide: your AWS account, start to finish"
source_notion_id: "3fd1e819-9813-81ea-a7c9-cfc078a6b2bb"
source_url: "https://thefintechers.notion.site/3fd1e819981381eaa7c9cfc078a6b2bb"
fetched_at: "2026-10-19T19:04:41.517Z"
category: "guide"
---

# AWS Participant Guide: your AWS account, start to finish

> ⚠️

**Must-read for every hacker.** Prepared by AWS and Deloitte. Every team gets its own AWS account with Amazon Bedrock, a **USD 800 budget** and admin rights inside it. This page covers signing in, calling models from code, watching your spend, and the four things that are deliberately blocked. **Bring a phone:** multi-factor authentication is required.


### ⚡ Quick reference


| Access portal | [https://d-c3676ff6eb.awsapps.com/start](https://d-c3676ff6eb.awsapps.com/start) |
| --- | --- |
| Build everything in | `eu-central-1` (Frankfurt) |
| Voice models only | `eu-north-1` (Nova Sonic) |
| SSO region for the CLI | `eu-north-1` ← deliberately different |
| Your role | `ai-hackathon-TeamAdmin` |
| Session length | 12 hours |
| Team budget | USD 800, shared across your team |
| Shared datasets | `s3://ai-hackathon-datasets-422928733782/` |


### 🔑 Signing in the first time

1. **Open the portal and enter your email.** Use the address you registered with. There is no password to find; you have never been given one.
1. **Collect the one-time code from your inbox.** Your first sign-in attempt triggers the email, so nothing is waiting before that. The code is short-lived; if you leave it an hour, start again.
1. **Register an authenticator app.** Scan the QR code with Google Authenticator, 1Password, Authy or similar. You need it every time you sign in, so use a device you have at the venue.
1. **Choose your account and role.** You see your team's account with `ai-hackathon-TeamAdmin`, plus read-only access to a shared account with datasets. Pick TeamAdmin.
> 🌍

**Set your region immediately.** The console remembers the last region you used, and the region selector is the most common cause of mysterious permission errors. Set **Europe (Frankfurt) eu-central-1** before you create anything.


### 💻 Working from the command line

There are no access keys in this environment. The CLI works through SSO, which gives short-lived credentials that refresh with one command.

**One-time setup:** run `aws configure sso` and answer:


| Prompt | Answer |
| --- | --- |
| SSO session name | `hackathon` |
| SSO start URL | [https://d-c3676ff6eb.awsapps.com/start](https://d-c3676ff6eb.awsapps.com/start) |
| SSO region | `eu-north-1` (where sign-in lives) |
| SSO registration scopes | accept the default |
| CLI default client region | `eu-central-1` (where your work lives) |
| CLI default output format | `json` |

> ❗

**"No instances found"?** You entered eu-central-1 as the SSO region. It is **eu-north-1**: you build in Frankfurt, but the sign-in directory lives in Stockholm.

**Every day after that:**

```Bash
aws sso login --profile hackathon
aws sts get-caller-identity   # confirms which account you are in
```

Sessions last 12 hours, so run `aws sso login` about once a day, including once during the overnight stretch.

**Faster for one-off commands:** in the access portal, next to your account, choose **Access keys** to get temporary credentials for your shell. They expire with your session.

> 🔐

**For anything long-running, use an IAM role.** Pasted credentials expire and break running services. Give Lambda, ECS and EC2 an IAM role instead (creating roles is allowed). If you are about to commit a secret, attach a role.


### 🤖 Calling models on Bedrock

Model access is already enabled. Nothing to request.


#### Claude

In Europe, Claude runs through EU cross-region inference profiles, so the model ID needs the `**eu.**`** prefix**. A bare `anthropic.claude-…` ID will not work. Prices per million tokens (input / output). Rate limits are shared across your team.


| Model ID | In / out | Tokens/min | Requests/min |
| --- | --- | --- | --- |
| `eu.anthropic.claude-haiku-4-5-20251001-v1:0` | USD 1.10 / 5.50 | 5M | 50 |
| `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` | USD 3.30 / 16.50 | 5M | 50 |
| `eu.anthropic.claude-opus-4-5-20251101-v1:0` | USD 5.50 / 27.50 | 2M | 25 |

> 🚫

**Claude 5 is not available, don't lose time on it.** Sonnet 5, Opus 5 and Sonnet 5.5 have no capacity in this region and return "AccessDeniedException … not available for this account". A mentor cannot switch this on. Use Sonnet 4.5 or Opus 4.5.


#### Everything else

No prefix needed, effectively unlimited throughput (100M tokens/min), good for high-volume loops and evaluation runs: `qwen.qwen3-235b-a22b-2507-v1:0`, `qwen.qwen3-32b-v1:0`, `qwen.qwen3-coder-30b-a3b-v1:0`, `zai.glm-4.7-flash`, `nvidia.nemotron-super-3-120b`, `mistral.devstral-2-123b`, `minimax.minimax-m2.5`, `openai.gpt-oss-120b-1:0`, `openai.gpt-oss-20b-1:0`.

Amazon Nova and Pixtral use EU profiles with lower limits: `eu.amazon.nova-2-lite-v1:0` (8M), `eu.amazon.nova-pro-v1:0` (2M), `eu.amazon.nova-micro-v1:0` and `eu.amazon.nova-lite-v1:0` (400K), `eu.mistral.pixtral-large-2502-v1:0` (80K).


#### Voice: Nova Sonic, the one exception to Frankfurt

Speech-to-speech models are only in Stockholm: `amazon.nova-2-sonic-v1:0` (speech in, speech + text out) and `amazon.nova-2-5-sonic` (speech + text in, speech + text out), both with `--region eu-north-1`. They use the bidirectional streaming API (`InvokeModelWithBidirectionalStream`), not Converse.

> 📍

**Keep your data in Frankfurt.** Only the model call goes to Stockholm. S3 buckets, Lambdas and everything else stay in eu-central-1. Transcribe and Polly are blocked in eu-north-1; if you want Transcribe, run it in eu-central-1.


#### A first call

```Bash
aws bedrock-runtime converse \
  --region eu-central-1 \
  --model-id eu.anthropic.claude-sonnet-4-5-20250929-v1:0 \
  --messages '[{"role":"user","content":[{"text":"Say hello"}]}]' \
  --inference-config '{"maxTokens":100}'
```

In Python: `boto3.client("bedrock-runtime", region_name="eu-central-1")` and the same `converse` call. To see everything available: `aws bedrock list-inference-profiles --region eu-central-1`.

> 💸

**Prompt caching is the cheapest optimisation you will make.** Cached input tokens cost ten times less (USD 0.33 vs 3.30 per million on Sonnet 4.5). If your agent resends the same system prompt or document every turn, cache it.


### 🗂️ Shared datasets

Everything the track owners hand over is in one bucket, readable from your own account (no extra credentials, no account switching):

```Bash
aws s3 ls s3://ai-hackathon-datasets-422928733782/ --region eu-central-1
```

The bucket is **read-only on purpose**: nobody can alter a dataset other teams are judged on. Copy what you need into your own account.


| Folder | What is in it | Best for |
| --- | --- | --- |
| `CNB/` | Synthetic AML data. `clients.csv` (5,493 rows, 12 columns: contract date and channel, PEP flag, client type, expected vs actual volume and count for 2Q2026, AML risk score low/medium/high) and `transactions.csv` (397,853 rows, 11 columns, joins on client ID). Semicolon-delimited, UTF-8 with BOM. No real names or accounts | Track 5 (AML challenges) |
| `MerchantKYB/` | Eight PDFs: merchant application forms A and B, partner application, UBO declaration and checklist, short-form merchant agreement. Pair with `Required-Documents-Checklist.pdf` for a completeness check | Track 4 (Tapaya KYB challenge) |
| `MostlyRIght/` | EU financial firm licences and warnings: ČNB and ESMA MiCA licence registers, EPC SEPA Instant and Verification of Payee participants, AMF and ESMA warnings, EU sanctions (entities only) | Tracks 1, 4, 5 |

```Python
import pandas as pd
clients = pd.read_csv("clients.csv", sep=";")
txns = pd.read_csv("transactions.csv", sep=";")
df = txns.merge(clients, on="client ID")
```

**MoroSystems TSYS API:** an external payments API with its own documentation portal ([https://tsys-docs.morosystems.cloud](https://tsys-docs.morosystems.cloud)) and API ([https://tsys-api.morosystems.cloud](https://tsys-api.morosystems.cloud)), for teams that want a live integration target. A shared demo key is issued for this event; you get the login and API key at tech onboarding and on Circle. Read the portal before guessing at endpoints.


### 💰 Watching your spend

Your team has **USD 800**, shared across everyone in your account. Nothing cuts you off: the budget alerts the organisers, it does not stop you.

> 🧾

**The billing console will not open, use the CLI.** Cost Explorer in the browser is switched off at account level, so don't ask for permissions. The data is available over the API (in `us-east-1`, the one exception to Frankfurt):

```Bash
# What have we spent?
aws ce get-cost-and-usage --region us-east-1 \
  --time-period Start=2026-10-01,End=2026-10-21 \
  --granularity MONTHLY --metrics UnblendedCost \
  --query 'ResultsByTime[0].Total.UnblendedCost.Amount' --output text

# Which model is eating the budget?
aws ce get-cost-and-usage --region us-east-1 \
  --time-period Start=2026-10-01,End=2026-10-21 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount!=`0`].[Keys[0],Metrics.UnblendedCost.Amount]' \
  --output table
```

* You only see your own account. No team sees another's spend.
* Figures lag by up to 24 hours. It is a review tool, not a live meter.
* Amounts under a cent show as 0. On day one it looks like nothing is recorded; it is.
* Output tokens dominate. Draft with Haiku and escalate to Opus only where it matters.

### 🚧 What's blocked, and why

Guardrails are enforced at account level, so an error is final. There is no local workaround.

1. **Regions other than Frankfurt.** Everything you create lives in eu-central-1. A tutorial that says us-east-1 needs changing.
1. **IAM users and access keys.** Long-lived keys leaked in public repos are the classic hackathon incident. Use IAM roles instead (allowed).
1. **Large and GPU instances.** Available: t3.*, t4g.*, m6i.large, m6i.xlarge, m7g.large, m7g.xlarge, c6i.large, c7g.large. Inference runs on Bedrock, so no GPU is needed; talk to a mentor first if you think you need one.
1. **Services that bill while idle.** Reserved instances, capacity reservations, savings plans, dedicated hosts, Redshift, MSK/Kafka, EMR, Outposts, Snowball, Braket, domain registration and Shield Advanced are unavailable.
> 🧲

**Vector stores are open, with one cost trap.** OpenSearch, RDS with pgvector and Bedrock Knowledge Bases are available. A provisioned `t3.small.search` OpenSearch domain costs about USD 1 a day; **OpenSearch Serverless costs about USD 23 a day** whether you query it or not. Pick provisioned, and delete it before you leave.


### 🛠️ When something fails


| What you see | What it means | Fix |
| --- | --- | --- |
| "explicit deny in a service control policy", ARN shows a region other than eu-central-1 | Console or CLI pointed at the wrong region | You: switch to Frankfurt and retry |
| "explicit deny in a service control policy", ARN says eu-central-1 | A gap in the guardrails, not your mistake | Organiser: report it with the full message |
| "no instances found" during `aws configure sso` | SSO region entered as eu-central-1 | You: it is eu-north-1 |
| "not available for this account" on a Claude 5 model | No capacity in Europe | You: use Sonnet 4.5 or Opus 4.5 |
| ValidationException on `anthropic.claude-…` | Missing the EU profile prefix | You: prepend `eu.` |
| ThrottlingException | Team hit the shared limit (50 requests/min, 25 on Opus) | You: back off, stagger jobs, move bulk work to Qwen or Nova |
| Cannot create an access key | Blocked by design | You: `aws sso login`, or a role for running code |
| Credentials stopped working | The 12-hour session ended | You: `aws sso login` again |
| Cost Explorer shows 0 | Sub-cent rounding or the 24-hour lag | You: normal, check later |

When you ask for help, paste the complete error message: the region in the ARN and the exact action name make it diagnosable in seconds.


### 🏁 Before you leave

* **Push your code somewhere you own.** Accounts are frozen after the event; you keep read access to export, but don't rely on it.
* **Delete anything that bills while idle:** OpenSearch domains and collections, RDS instances, load balancers, NAT gateways. Freezing stops new resources, not the meter on existing ones.
* **Submission:** a repo link by the **code freeze, Tuesday 20 October at 13:30** (see Submission and judging in the hackers guide). No video or one-pager is required for the main judging.
