# -*- coding: utf-8 -*-
"""
app.py — Interactive Streamlit Dashboard for PerDiemo Copilot.

Designed for The FinTechers Hackathon 2026 (Prague):
- TRACK 01: Agentic Payments & Money Movement (MoroSystems Payments Sandbox & Conversational Ops)
- TRACK 06: Finance Operations & Back-Office AI (Komerční banka Compliance & Statutory Per Diems)
"""
import os
import json
import importlib
import streamlit as st
import pandas as pd

import perdiemo_client
import agent_intake
import backoffice_auditor
import morosystems_client

# Hot reload submodules to bust Streamlit process cache
importlib.reload(perdiemo_client)
importlib.reload(agent_intake)
importlib.reload(backoffice_auditor)
importlib.reload(morosystems_client)

from perdiemo_client import PerDiemoClient
from agent_intake import BedrockIntakeAgent
from backoffice_auditor import BackOfficeAuditor
from morosystems_client import MoroSystemsPaymentClient

# Streamlit Page Config
st.set_page_config(
    page_title="PerDiemo Copilot — Agentic Travel Reconciler & Payout",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.9rem;
        text-align: center;
    }
    .badge-passed {
        color: #166534;
        background-color: #dcfce7;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-critical {
        color: #991b1b;
        background-color: #fee2e2;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-warning {
        color: #854d0e;
        background-color: #fef9c3;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-info {
        color: #1e40af;
        background-color: #dbeafe;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-financial {
        color: #5b21b6;
        background-color: #ede9fe;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .rule-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .rule-tag {
        font-family: monospace;
        font-weight: 700;
        color: #0f172a;
        background-color: #f1f5f9;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .settlement-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    .finding-item {
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
        border-radius: 8px;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .finding-item-passed {
        background-color: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.25);
        border-left: 5px solid #22c55e;
    }
    .finding-item-warning {
        background-color: rgba(234, 179, 8, 0.14);
        border: 1px solid rgba(234, 179, 8, 0.25);
        border-left: 5px solid #eab308;
    }
    .finding-item-critical {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 5px solid #ef4444;
    }
    .finding-item-info {
        background-color: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 5px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services (no stale cache across edits)
def get_services():
    client = PerDiemoClient()
    agent = BedrockIntakeAgent()
    auditor = BackOfficeAuditor()
    moro_client = MoroSystemsPaymentClient()
    return client, agent, auditor, moro_client

client, agent, auditor, moro_client = get_services()

def render_audit_finding(finding):
    if isinstance(finding, str):
        finding = {"severity": "INFO", "rule": "KB-INFO", "message": finding}
    sev = str(finding.get("severity", "INFO")).upper()
    rule = finding.get("rule", "KB-RULE")
    msg = finding.get("message", "")

    if sev == "PASSED":
        cls = "finding-item-passed"
        badge = '<span class="badge-passed">PASSED</span>'
    elif sev == "WARNING":
        cls = "finding-item-warning"
        badge = '<span class="badge-warning">WARNING</span>'
    elif sev == "CRITICAL":
        cls = "finding-item-critical"
        badge = '<span class="badge-critical">CRITICAL</span>'
    else:
        cls = "finding-item-info"
        badge = '<span class="badge-info">INFO</span>'

    st.markdown(f"""
        <div class="finding-item {cls}">
            <div style="flex-shrink: 0; margin-top: 1px;">{badge}</div>
            <div style="flex-grow: 1;">
                <span class="rule-tag">{rule}</span> &nbsp;{msg}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 1.6rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>⚖️</span> <span>PerDiemo Copilot</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">
                Autonomous Reconciler & Payout Agent
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏆 FinTechers Hackathon 2026")
    st.markdown("🎯 **Track 01:** Agentic Payments & Money Movement")
    st.markdown("🛡️ **Track 06:** KB Back-Office AI & Statutory Controls")
    st.divider()

    st.markdown("#### ⚙️ Service Integrations")
    try:
        health = client.health()
        st.success(f"PerDiemo API: Online (v{health.get('version', '1.0')})")
    except Exception:
        st.warning("PerDiemo API: Cloud Connecting...")

    if moro_client.mock_mode:
        st.info("MoroSystems Sandbox: Ready (Adapter Mode)")
    else:
        st.success("MoroSystems API: Connected Live")

    st.markdown(f"**AWS Region:** `{agent.region_name}`")
    model_name = agent.model_id
    if "claude-sonnet-4-5" in model_name:
        model_display = "Claude Sonnet 4.5 (Bedrock)"
    elif "claude-haiku-4-5" in model_name:
        model_display = "Claude Haiku 4.5 (Bedrock)"
    else:
        model_display = model_name.split(":")[-2].split(".")[-1] if ":" in model_name else model_name
    st.markdown(f"**Bedrock LLM:** `{model_display}`")

    st.divider()
    st.markdown("#### 📜 Legislative Standards")
    st.caption("• Czech Labour Code §§ 151–189 ZP")
    st.caption("• Supreme Admin Court: NSS 3 Afs 97/2025 - 71")
    st.caption("• ČNB Foreign Exchange Daily Fixing")

    with st.expander("🛡️ KB Rules Quick Index (7 Rules)", expanded=False):
        st.markdown("""
        - <span class="badge-critical">CRIT</span> `KB-RULE-01-MEAL-DOUBLE-DIPPING`
        - <span class="badge-warning">WARN</span> `KB-RULE-02-WEEKEND-TRAVEL`
        - <span class="badge-critical">CRIT</span> `KB-RULE-03-AUDIT-FINGERPRINT`
        - <span class="badge-info">INFO</span> `KB-RULE-04-CARD-RECONCILIATION`
        - <span class="badge-financial">FIN</span> `KB-FIN-STATUTORY-ALLOWANCE`
        - <span class="badge-financial">FIN</span> `KB-FIN-OUT-OF-POCKET-CASH`
        - <span class="badge-financial">FIN</span> `KB-FIN-PERSONAL-CARD-OFFSET`
        """, unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-header">💳 PerDiemo Copilot — Self-Reconciling Travel Card & Payouts</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Feed corporate card streams, auto-cluster business trips, compute statutory Czech per diems, and disburse exact reimbursements via MoroSystems payments rails.</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab_card, tab_doc, tab_rules = st.tabs([
    "💳 1. Proactive Corporate Card Auto-Reconciliation & Payout (Track 01)",
    "📄 2. Document & Receipt Compliance Audit (Track 06)",
    "🛡️ 3. Komerční Banka Compliance & Audit Rules Matrix"
])

# ==============================================================================
# TAB 1: Proactive Corporate Card Stream & Money Movement (Track 01)
# ==============================================================================
with tab_card:
    st.markdown("### Proactive Corporate Card Stream Ingestion (TSYS Sandbox)")
    
    # Session state for TSYS feed
    if "tsys_data" not in st.session_state:
        tsys_path = os.path.join(os.path.dirname(__file__), "sample_data", "tsys_card_feed.json")
        if os.path.exists(tsys_path):
            with open(tsys_path, encoding="utf-8") as f:
                st.session_state["tsys_data"] = json.load(f)
        else:
            st.session_state["tsys_data"] = {"transactions": [], "out_of_pocket_cash": []}

    # Dynamic Bedrock Generation Bar
    with st.expander("🎲 Generate Dynamic Card Stream on the fly via AWS Bedrock", expanded=True):
        g_col1, g_col2, g_col3 = st.columns([2, 1, 2])
        dest_list = [
            "Berlin", "Vienna", "Zurich", "London", "Paris", "Munich",
            "Frankfurt", "Warsaw", "Bratislava", "Milan", "Amsterdam", "Brussels", "Budapest"
        ]
        dest_choice = g_col1.selectbox("Target Business Destination:", dest_list, index=0)
        days_choice = g_col2.number_input("Trip Duration (Days):", min_value=2, max_value=7, value=3)
        if g_col3.button("✨ Query Bedrock to Generate Fresh Card Stream", use_container_width=True):
            with st.spinner(f"🤖 Calling Bedrock (Claude Sonnet 4.5) to synthesize fresh card stream for {dest_choice}..."):
                fresh_feed = agent.generate_card_stream(
                    traveler_name="Alex Miller",
                    destination=dest_choice,
                    num_days=days_choice
                )
                st.session_state["tsys_data"] = fresh_feed
                st.session_state.pop("card_settlement", None)
                st.session_state.pop("payout_receipt", None)
                st.success(f"Generated {len(fresh_feed.get('transactions', []))} fresh card transactions for {dest_choice}!")

    tsys_data = st.session_state["tsys_data"]
    col_tx, col_recon = st.columns([1, 1], gap="large")

    with col_tx:
        st.markdown("#### 📥 Live Card Transactions")
        st.caption(f"Employee: **{tsys_data.get('cardholder', 'Alex Miller')}** | Account: `{tsys_data.get('account_id')}` | IBAN: `{tsys_data.get('employee_iban')}`")
        
        tx_list = tsys_data.get("transactions", [])
        if tx_list:
            cols_avail = [c for c in ["timestamp", "merchant_name", "amount", "currency", "mcc_category", "expense_type"] if c in pd.DataFrame(tx_list).columns]
            df_display = pd.DataFrame(tx_list)[cols_avail]
            if "timestamp" in df_display.columns:
                df_display["timestamp"] = df_display["timestamp"].astype(str).str.replace("T", " ")
            st.dataframe(df_display, use_container_width=True, height=280)

        st.markdown("#### 💵 Out-of-Pocket Cash Claims (Non-Card)")
        st.caption("ℹ️ *Non-card expenses paid with employee's own cash (e.g. taxi without card terminal) requiring employer reimbursement alongside per diems.*")
        oop_list = tsys_data.get("out_of_pocket_cash", [])
        for oop in oop_list:
            st.info(f"🧾 **{oop.get('merchant_name')}**: {oop.get('amount')} {oop.get('currency')} (Method: {oop.get('payment_method')}) — *{oop.get('notes')}*")

        run_recon_btn = st.button("🤖 Run Proactive Agent Trip Clustering & Settlement", type="primary", use_container_width=True)

    with col_recon:
        st.markdown("#### 🧠 Agentic Trip Detection & Statutory Reconciliation")

        if run_recon_btn or "card_settlement" in st.session_state:
            if run_recon_btn:
                with st.spinner("🤖 AWS Bedrock clustering raw card transactions into trip itinerary..."):
                    clustered = agent.cluster_card_stream(tx_list, tsys_data.get("cardholder", "Alex Miller"))
                    stat_itinerary = clustered.get("statutory_itinerary", {})
                
                with st.spinner("⚖️ PerDiemo Cloud Engine calculating statutory allowances & ČNB fixing..."):
                    trips_payload = [{
                        "id_cesty": "TSYS-KB-AUTO-001",
                        "ucel_cesty": stat_itinerary.get("ucel_cesty", "Business"),
                        "vlastnictvi_vozidla": stat_itinerary.get("typ_vozidla", "SLUZEBNI"),
                        "zamestnanec_jednatel": stat_itinerary.get("zamestnanec_jednatel", "Alex Miller"),
                        "spolecnost": stat_itinerary.get("spolecnost", "KB Enterprise Client"),
                        "bezplatna_strava": stat_itinerary.get("bezplatna_strava", {}),
                        "itinerar": stat_itinerary.get("itinerary", [])
                    }]
                    calc_result = client.calculate(trips_payload, year=2025)

                with st.spinner("🛡️ Reconciling company card spend, personal charges, and cash receipts..."):
                    settlement = auditor.reconcile_and_settle(
                        stat_itinerary,
                        calc_result,
                        tx_list,
                        oop_list
                    )

                st.session_state["card_settlement"] = {
                    "clustered": clustered,
                    "calc": calc_result,
                    "settlement": settlement
                }

            # Retrieve state
            s_state = st.session_state["card_settlement"]
            clustered = s_state["clustered"]
            stat_itinerary = clustered.get("statutory_itinerary", {})
            calc_result = s_state["calc"]
            settlement = s_state["settlement"]
            net = settlement["net_settlement"]
            trip_info = clustered.get("detected_trip", {})

            st.success(f"📍 **Detected Trip:** {trip_info.get('destination_city')}, {trip_info.get('destination_country')} ({trip_info.get('start_time')[:10]} to {trip_info.get('end_time')[:10]})")
            st.caption(f"_{trip_info.get('summary')}_")

            hotel_info = stat_itinerary.get("hotel_info", {})
            h_name = hotel_info.get("hotel_name", "Local Accommodation")
            st.caption(f"🏨 **Detected Lodging:** {h_name} (Room-only card charge — full statutory per diem preserved with 0% meal deduction).")

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Statutory Per Diem", f"{net.get('statutory_per_diem_czk', 0):,.2f} CZK")
            m2.metric("Out-of-Pocket Cash", f"+{net.get('out_of_pocket_czk', 0):,.2f} CZK")
            m3.metric("Personal Card Offset", f"-{net.get('personal_card_offset_czk', 0):,.2f} CZK")

            # Net Settlement Card
            payout_amount = net.get("net_reimbursement_czk", 0.0)
            st.markdown(f"""
                <div class="settlement-card">
                    <div style="font-size: 0.85rem; color: #166534; font-weight: 700; text-transform: uppercase;">
                        Net Employee Reimbursement Calculated
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 4px 0;">
                        {payout_amount:,.2f} CZK
                    </div>
                    <div style="font-size: 0.85rem; color: #334155;">
                        Target IBAN: <code>{tsys_data.get('employee_iban')}</code> (Alex Miller)
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Audit findings
            with st.expander("🔍 View Compliance Audit Findings & Cryptographic Seal", expanded=False):
                for f in settlement.get("findings", []):
                    render_audit_finding(f)
                sig = settlement.get("verification_signature")
                if sig:
                    st.markdown('<div style="font-size: 0.78rem; font-weight: 700; color: #64748b; margin-top: 0.9rem; text-transform: uppercase;">🔒 Cryptographic Evidentiary Audit Seal (SHA-256):</div>', unsafe_allow_html=True)
                    st.code(sig, language="text")

            # MoroSystems Execution Gate
            st.markdown("#### 🚀 MoroSystems Payments Sandbox Execution")
            st.caption("Track 01 Guardrail: The agent requires human confirmation before executing write actions.")

            if st.button(f"💸 Authorize Instant Payout of {payout_amount:,.2f} CZK via MoroSystems Rail", type="primary", use_container_width=True):
                with st.spinner("Executing payment order on MoroSystems sandbox..."):
                    payout_resp = moro_client.execute_payout(
                        recipient_name=tsys_data.get("cardholder", "Alex Miller"),
                        recipient_iban=tsys_data.get("employee_iban", "CZ6501000000001928374650"),
                        amount=payout_amount,
                        currency="CZK",
                        traveler_id=tsys_data.get("employee_id", "EMP-KB-0042"),
                        trip_reference=f"{trip_info.get('destination_city', 'Business')} Trip ({trip_info.get('start_time', '')[:10]})",
                        explanation_log=settlement.get("explanation_log", {}),
                        audit_seal=settlement.get("verification_signature", "MOCK-SEAL")
                    )
                    st.session_state["payout_receipt"] = payout_resp

            # Display Payment Receipt
            if "payout_receipt" in st.session_state:
                receipt = st.session_state["payout_receipt"]
                st.success(f"🎉 **PAYMENT SETTLED!** {receipt.get('message')}")
                r_col1, r_col2 = st.columns(2)
                r_col1.markdown(f"**Payment ID:** `{receipt.get('payment_id')}`")
                r_col1.markdown(f"**Clearing System:** `{receipt.get('clearing_system')}`")
                r_col2.markdown(f"**Settled At:** `{receipt.get('settled_at')}`")
                r_col2.markdown(f"**Verification Hash:** `{receipt.get('transfer_verification_hash')[:16]}...`")
        else:
            st.info("👈 Click **'🤖 Run Proactive Agent Trip Clustering & Settlement'** to cluster these raw card transactions into an auditable business trip, calculate statutory allowances, and reconcile expenses.")

    # Conversational Payment Ops Chatbot (Multi-Turn Thread History)
    st.divider()
    st.markdown("### 💬 Conversational Payment Operations (Bedrock Claude Multi-Turn Copilot)")
    st.caption("Ask questions about this trip, fee breakdowns, statutory rates, or payment statuses. Maintains full conversation memory with Amazon Bedrock Claude Sonnet 4.5.")

    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = [
            {
                "role": "assistant",
                "content": "👋 Hi Alex, I'm **PerDiemo Copilot**. I have analyzed your corporate card transactions and reconciled your business travel per diems. Ask me anything about this trip, fee breakdowns, foreign exchange fixing, or corporate card offsets."
            }
        ]

    # Render complete chat history in dedicated container above input box
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_thread"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_query = st.chat_input("Ask PerDiemo Copilot (e.g. Why was KB-RULE-04 triggered? What is my net payout?)...")
    if user_query:
        # Append user message
        st.session_state["chat_thread"].append({"role": "user", "content": user_query})

        # Context payload for Bedrock
        trip_ctx = {
            "destination": dest_choice if "dest_choice" in locals() else "Vienna",
            "tsys_data": tsys_data,
            "card_settlement": st.session_state.get("card_settlement")
        }

        # Render new turn into chat_container and query Bedrock
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)
            with st.chat_message("assistant"):
                with st.spinner("🤖 Claude Sonnet 4.5 thinking..."):
                    ai_reply = agent.conversational_chat(st.session_state["chat_thread"], trip_ctx)
                    st.markdown(ai_reply)

        # Append assistant message to thread history and rerun to lock input box at the bottom
        st.session_state["chat_thread"].append({"role": "assistant", "content": ai_reply})
        st.rerun()

# ==============================================================================
# TAB 2: Document & Receipt Compliance Audit (Track 06)
# ==============================================================================
with tab_doc:
    st.markdown("### 1. Document & Trip Intake (Komerční Banka Back-Office)")
    col_input_doc, col_audit_doc = st.columns([1, 1], gap="large")

    with col_input_doc:
        intake_mode = st.radio("Intake Source:", ["Sample Preset", "Free-form Text / Slack Log", "Document Upload (PDF/Image)"], horizontal=True, key="doc_radio")
        sample_text = (
            "Departed Prague on June 10, 2025 at 07:00 AM by company car to Vienna for client meetings. "
            "Crossed the border at Mikulov at 09:30 AM, arrived in Vienna at 11:00 AM. "
            "Overnight at Grand Hotel Wien with complimentary breakfast included in room rate. "
            "On June 11 departed Vienna at 16:00, crossed border back into Czechia at 17:30, arrived in Prague at 20:00."
        )
        if intake_mode == "Sample Preset":
            trip_text = st.text_area("Trip Description:", value=sample_text, height=120, key="doc_sample_area")
        elif intake_mode == "Free-form Text / Slack Log":
            trip_text = st.text_area("Trip Description:", placeholder="Paste Slack messages...", height=120, key="doc_free_area")
        else:
            uploaded_file = st.file_uploader("Upload Boarding Pass or Hotel Receipt:", type=["jpg", "png", "pdf"], key="doc_uploader")
            trip_text = sample_text

        year_select = st.selectbox("Statutory Tax Year:", [2026, 2025, 2024], index=1, key="doc_year")
        simulate_fraud = st.checkbox("⚠️ Simulate Compliance Anomaly (Hide Hotel Breakfast)", value=False, help="Uncheck declared breakfast to test Komerční banka's meal double-dipping fraud detector.", key="doc_fraud")
        process_doc_btn = st.button("🚀 Run Autonomous Document Audit", type="primary", use_container_width=True, key="doc_proc_btn")

    with col_audit_doc:
        st.markdown("### 2. Komerční Banka Audit Protocol")
        if process_doc_btn or "doc_audit_result" in st.session_state:
            if process_doc_btn:
                with st.spinner("🤖 Bedrock Agent extracting structured statutory itinerary..."):
                    extracted = agent.extract_from_text(trip_text)
                    if simulate_fraud:
                        extracted["bezplatna_strava"] = {}
                        extracted["hotel_info"]["breakfast_included"] = True

                with st.spinner("⚖️ Computing allowances via PerDiemo Cloud Engine..."):
                    trips_payload = [{
                        "id_cesty": "KB-DOC-AUDIT-001",
                        "ucel_cesty": extracted.get("ucel_cesty", "Business"),
                        "vlastnictvi_vozidla": extracted.get("typ_vozidla", "SLUZEBNI"),
                        "zamestnanec_jednatel": extracted.get("zamestnanec_jednatel", "Alex Miller"),
                        "spolecnost": extracted.get("spolecnost", "KB Enterprise Client"),
                        "bezplatna_strava": extracted.get("bezplatna_strava", {}),
                        "itinerar": extracted.get("itinerary", [])
                    }]
                    calc_result = client.calculate(trips_payload, year=year_select)

                with st.spinner("🛡️ Running KB compliance rules..."):
                    audit_report = auditor.audit_trip(extracted, calc_result)

                st.session_state["doc_audit_result"] = {
                    "extracted": extracted,
                    "calc": calc_result,
                    "audit": audit_report
                }

            doc_res = st.session_state["doc_audit_result"]
            audit_report = doc_res["audit"]
            meta = doc_res["calc"].get("metadata", {})

            verdict = audit_report.get("verdict")
            score = audit_report.get("risk_score", 0)
            if verdict == "APPROVED":
                st.success(f"✅ VERDICT: **APPROVED FOR REIMBURSEMENT** (Risk Score: {score}/100)")
            elif verdict == "FLAGGED_FOR_REVIEW":
                st.warning(f"⚠️ VERDICT: **FLAGGED FOR ACCOUNTANT REVIEW** (Risk Score: {score}/100)")
            else:
                st.error(f"❌ VERDICT: **EXPENSE REJECTED** (Risk Score: {score}/100)")

            m1, m2, m3 = st.columns(3)
            m1.metric("Net Stravné", f"{meta.get('total_stravne_czk', 0):,.2f} CZK")
            m2.metric("Meal Deductions", f"-{meta.get('total_kraceni_czk', 0):,.2f} CZK")
            m3.metric("Pocket Money", f"{meta.get('total_kapesne_czk', 0):,.2f} CZK")

            st.markdown("#### 🔍 Compliance Audit Findings")
            for finding in audit_report.get("findings", []):
                render_audit_finding(finding)

            st.divider()
            st.markdown(f"**🔒 Cryptographic Audit Seal (SHA-256):**")
            st.code(meta.get("verification_signature", "N/A"), language="text")
            st.button("📥 Export Protocol to Pohoda XML / Accounting", type="secondary", use_container_width=True)

# ==============================================================================
# TAB 3: Komerční Banka Compliance & Audit Rules Matrix
# ==============================================================================
with tab_rules:
    st.markdown("### 🛡️ Komerční Banka Compliance, Audit & Fraud Prevention Rules")
    st.caption("Complete register of automated statutory rules, fraud detection models, and financial settlement algorithms running inside the PerDiemo Autonomous Agent.")

    # Top metrics
    rc1, rc2, rc3, rc4 = st.columns(4)
    rc1.metric("Active Compliance Rules", "4 Rules", "Statutory & Fraud")
    rc2.metric("Financial Settlement Rules", "3 Rules", "Reconciliation & Offsets")
    rc3.metric("Statutory Baseline", "§§ 151–189 ZP", "Czech Labour Code")
    rc4.metric("Evidentiary Standard", "NSS 3 Afs 97/2025", "SHA-256 Signed")

    st.markdown("---")

    # Filter choice
    rule_category = st.radio(
        "Filter Rules by Operational Domain:",
        [
            "All Rules (7 Total)",
            "Core Compliance & Fraud Rules (4)",
            "Financial Balancing & Offset Rules (3)",
            "Decision Matrix & Risk Thresholds"
        ],
        horizontal=True
    )

    st.markdown("")

    # If Decision Matrix or All
    if rule_category in ["All Rules (7 Total)", "Decision Matrix & Risk Thresholds"]:
        with st.container():
            st.markdown("#### ⚖️ Back-Office Decision Matrix & Risk Score Thresholds")
            st.markdown("""
            Every travel expense claim and clustered card stream is evaluated deterministically against the weighted risk scoring engine.
            The cumulative risk score ranges from **0 to 100 points**:
            """)
            dm1, dm2, dm3 = st.columns(3)
            with dm1:
                st.markdown("""
                <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1rem; text-align: center;">
                    <div style="font-weight: 800; color: #166534; font-size: 1.1rem;">APPROVED</div>
                    <div style="font-size: 0.85rem; color: #334155; margin-top: 4px;">Risk Score &lt; 40</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 6px;">
                        Full automated clearance. Dispatched instantly to MoroSystems payout rail or Pohoda XML accounting export.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with dm2:
                st.markdown("""
                <div style="background-color: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 1rem; text-align: center;">
                    <div style="font-weight: 800; color: #854d0e; font-size: 1.1rem;">FLAGGED FOR REVIEW</div>
                    <div style="font-size: 0.85rem; color: #334155; margin-top: 4px;">40 &le; Risk Score &lt; 70</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 6px;">
                        Minor anomalies detected (e.g. weekend travel without explicit rationale). Routed to human back-office controller queue.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with dm3:
                st.markdown("""
                <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; text-align: center;">
                    <div style="font-weight: 800; color: #991b1b; font-size: 1.1rem;">REJECTED</div>
                    <div style="font-size: 0.85rem; color: #334155; margin-top: 4px;">Risk Score &ge; 70</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 6px;">
                        Severe statutory violation or missing cryptographic seal. Automatic reimbursement execution is hard-blocked.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("")

    # Compliance Rules (4)
    if rule_category in ["All Rules (7 Total)", "Core Compliance & Fraud Rules (4)"]:
        st.markdown("#### 🛡️ Core Compliance & Fraud Prevention Rules")

        # RULE 01
        with st.expander("🔴 **KB-RULE-01-MEAL-DOUBLE-DIPPING** — Complimentary Meal Double-Dipping Audit", expanded=True):
            r1_c1, r1_c2 = st.columns([3, 1])
            with r1_c1:
                st.markdown("""
                * **Operational Mission:** Prevents fraudulent double expense claiming. When an employer pays for hotel accommodation that provides free breakfast, the statutory daily per diem must be reduced accordingly.
                * **Statutory Reference:** *Zákon č. 262/2006 Sb. (Zákoník práce), §§ 163 & 170 ZP*.
                * **Trigger Logic:** Triggered when lodging records or hotel invoice folios indicate breakfast was included in the corporate room charge, but the traveler did not declare `snidane` under `bezplatna_strava`.
                * **Card Stream Behavior (Track 01):** Standard POS card feeds carry merchant descriptors (MCC 7011) without Level 3 line items. At this card-stream stage, charges default to room-only (0% meal reduction, full statutory per diem preserved).
                """)
            with r1_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-critical">CRITICAL</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #991b1b; margin-top: 6px;">+45 Risk</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Statutory Tax Violation</div>
                </div>
                """, unsafe_allow_html=True)

        # RULE 02
        with st.expander("🟡 **KB-RULE-02-WEEKEND-TRAVEL-ANOMALY** — Weekend & Holiday Travel Justification Audit", expanded=True):
            r2_c1, r2_c2 = st.columns([3, 1])
            with r2_c1:
                st.markdown("""
                * **Operational Mission:** Identifies non-business personal travel disguised as corporate trips by auditing travel dates falling on Saturdays or Sundays.
                * **Statutory Reference:** *Zákon č. 262/2006 Sb., § 152 & § 156 ZP*.
                * **Trigger Logic:** Checks if any itinerary leg or card transaction occurs on a Saturday or Sunday. Evaluates `ucel_cesty` against verified commercial keywords (*conference, urgent, trade fair, veletrh, jednání, meeting, audit*).
                * **Mitigation:** If justified by valid business rationale, passes with informational clearance; otherwise adds +25 risk points and routes to controller.
                """)
            with r2_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-warning">WARNING</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #854d0e; margin-top: 6px;">+25 Risk</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Controller Review</div>
                </div>
                """, unsafe_allow_html=True)

        # RULE 03
        with st.expander("🔴 **KB-RULE-03-AUDIT-FINGERPRINT** — Cryptographic SHA-256 Evidentiary Seal", expanded=True):
            r3_c1, r3_c2 = st.columns([3, 1])
            with r3_c1:
                st.markdown("""
                * **Operational Mission:** Guarantees cryptographic immutability and audit defence in tax audits, where the employer bears the full burden of proof.
                * **Legal Precedent:** Supreme Administrative Court Decision *NSS 3 Afs 97/2025 - 71*.
                * **Trigger Logic:** Checks whether the statutory calculation payload contains a tamper-proof 64-character SHA-256 cryptographic signature issued by the statutory calculation engine.
                * **Enforcement:** If the calculation lacks a valid seal, the claim is assigned +50 risk points and hard-blocked from reimbursement.
                """)
            with r3_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-critical">CRITICAL</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #991b1b; margin-top: 6px;">+50 Risk</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Instant Hard-Block</div>
                </div>
                """, unsafe_allow_html=True)

        # RULE 04
        with st.expander("🔵 **KB-RULE-04-CARD-RECONCILIATION** — Corporate Credit Card Travel Window Matching", expanded=True):
            r4_c1, r4_c2 = st.columns([3, 1])
            with r4_c1:
                st.markdown("""
                * **Operational Mission:** Reconciles real-time corporate card transactions (TSYS / ISO 20022 Open Banking feeds) against the active travel window boundaries ($T_{\\text{start}}$ to $T_{\\text{end}}$).
                * **Industry Standard:** ISO 20022 Financial Data Interchange & Open Banking Reconciliation.
                * **Trigger Logic:** Evaluates transaction timestamps against departure and return dates. Confirms expenses occurred strictly during authorized business travel.
                * **Enforcement:** Reports exact count of matched transactions and flags any orphan expenses occurring outside the travel window.
                """)
            with r4_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-info">INFO</span>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #1e40af; margin-top: 6px;">0 Risk</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Cross-Validation</div>
                </div>
                """, unsafe_allow_html=True)

    # Financial Settlement Rules (3)
    if rule_category in ["All Rules (7 Total)", "Financial Balancing & Offset Rules (3)"]:
        st.markdown("#### 💳 Financial Balancing & Settlement Rules (`reconcile_and_settle`)")

        # FIN 01
        with st.expander("🟣 **KB-FIN-STATUTORY-ALLOWANCE** — Statutory Per Diem Daily Credit", expanded=True):
            f1_c1, f1_c2 = st.columns([3, 1])
            with f1_c1:
                st.markdown("""
                * **Operational Purpose:** Calculates the lawful daily allowance entitlement for foreign or domestic business travel.
                * **Statutory Reference:** *Zákon č. 262/2006 Sb., §§ 163, 170 & 183 ZP* and daily ČNB fixing exchange rates.
                * **Accounting Direction:** **`+ CREDIT`** to Employee Account.
                * **Mathematical Formula:** Base country statutory rate (e.g. 60 EUR/day in Germany) multiplied by official ČNB exchange fixing from the first day of travel, minus any applicable free meal deductions.
                """)
            with f1_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-financial">+ CREDIT</span>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #5b21b6; margin-top: 6px;">Per Diem Credit</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Labour Code §§ 163-170</div>
                </div>
                """, unsafe_allow_html=True)

        # FIN 02
        with st.expander("🟣 **KB-FIN-OUT-OF-POCKET-CASH** — Non-Card Cash Outlay Reimbursement", expanded=True):
            f2_c1, f2_c2 = st.columns([3, 1])
            with f2_c1:
                st.markdown("""
                * **Operational Purpose:** Reimburses legitimate business travel expenses paid out-of-pocket using personal cash (e.g. cash taxi when POS terminal was down, coin parking meters).
                * **Accounting Direction:** **`+ CREDIT`** to Employee Account.
                * **Trigger Criteria:** Transactions tagged with payment method `PERSONAL_CASH` with valid receipt justification.
                """)
            with f2_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-financial">+ CREDIT</span>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #5b21b6; margin-top: 6px;">Cash Reimburse</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Direct Out-of-Pocket</div>
                </div>
                """, unsafe_allow_html=True)

        # FIN 03
        with st.expander("🟣 **KB-FIN-PERSONAL-CARD-OFFSET** — Personal Spend Offset on Company Card", expanded=True):
            f3_c1, f3_c2 = st.columns([3, 1])
            with f3_c1:
                st.markdown("""
                * **Operational Purpose:** Automatically recovers company funds when an employee uses the corporate credit card for personal purchases (e.g. personal groceries at Rewe/Billa, pharmacy, or souvenirs).
                * **Accounting Direction:** **`- DEBIT`** from Employee Reimbursement Payout.
                * **Trigger Criteria:** Card transactions flagged with `expense_type == "PERSONAL_EXPENSE"` or non-business MCC categories.
                * **Automated Action:** Deducts the exact converted CZK amount directly from the statutory net payout, eliminating manual accounts receivable tracking.
                """)
            with f3_c2:
                st.markdown("""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem; text-align: center;">
                    <span class="badge-financial">- DEBIT OFFSET</span>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #991b1b; margin-top: 6px;">Auto-Recovery</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Direct Net Offset</div>
                </div>
                """, unsafe_allow_html=True)

    # Master Table view
    st.markdown("---")
    st.markdown("#### 📋 Master Rules Matrix Table")
    rules_data = [
        {"Rule ID": "KB-RULE-01-MEAL-DOUBLE-DIPPING", "Category": "Compliance", "Severity": "CRITICAL", "Risk Impact": "+45", "Legal Anchor": "§§ 163 & 170 ZP", "Action": "Flags free hotel breakfast not declared in per diem"},
        {"Rule ID": "KB-RULE-02-WEEKEND-TRAVEL-ANOMALY", "Category": "Compliance", "Severity": "WARNING", "Risk Impact": "+25", "Legal Anchor": "§ 152 & § 156 ZP", "Action": "Audits weekend travel for commercial justification"},
        {"Rule ID": "KB-RULE-03-AUDIT-FINGERPRINT", "Category": "Compliance", "Severity": "CRITICAL", "Risk Impact": "+50", "Legal Anchor": "NSS 3 Afs 97/2025", "Action": "Requires 64-char SHA-256 calculation seal"},
        {"Rule ID": "KB-RULE-04-CARD-RECONCILIATION", "Category": "Compliance", "Severity": "INFO", "Risk Impact": "0", "Legal Anchor": "ISO 20022 / TSYS", "Action": "Cross-references card transactions with travel dates"},
        {"Rule ID": "KB-FIN-STATUTORY-ALLOWANCE", "Category": "Financial", "Severity": "CREDIT", "Risk Impact": "N/A", "Legal Anchor": "§§ 163, 170, 183 ZP", "Action": "Calculates statutory per diem with ČNB daily FX"},
        {"Rule ID": "KB-FIN-OUT-OF-POCKET-CASH", "Category": "Financial", "Severity": "CREDIT", "Risk Impact": "N/A", "Legal Anchor": "Direct Reimburse", "Action": "Reimburses non-card personal cash expenses"},
        {"Rule ID": "KB-FIN-PERSONAL-CARD-OFFSET", "Category": "Financial", "Severity": "DEBIT", "Risk Impact": "N/A", "Legal Anchor": "Corporate Recovery", "Action": "Deducts personal card spend from net payout"}
    ]
    st.dataframe(pd.DataFrame(rules_data), use_container_width=True, hide_index=True)
