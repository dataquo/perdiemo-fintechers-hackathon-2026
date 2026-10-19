# -*- coding: utf-8 -*-
"""
app.py — Interactive Streamlit Dashboard for PerDiemo Copilot.
Designed for live demonstration at The FinTechers Hackathon 2026.
"""
import json
import streamlit as st
import pandas as pd
from perdiemo_client import PerDiemoClient
from agent_intake import BedrockIntakeAgent
from backoffice_auditor import BackOfficeAuditor

# Streamlit Page Config
st.set_page_config(
    page_title="PerDiemo Copilot — KB Back-Office AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .badge-passed {
        color: #166534;
        background-color: #dcfce7;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-critical {
        color: #991b1b;
        background-color: #fee2e2;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-warning {
        color: #854d0e;
        background-color: #fef9c3;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services
@st.cache_resource
def get_services():
    client = PerDiemoClient()
    agent = BedrockIntakeAgent()
    auditor = BackOfficeAuditor()
    return client, agent, auditor

client, agent, auditor = get_services()

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 1.7rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>⚖️</span> <span>PerDiemo</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">
                Statutory Travel Expense Copilot
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🏆 FinTechers Hackathon 2026")
    st.markdown("**Track 06:** Finance Operations & Back-Office AI")
    st.markdown("**Partner Target:** Komerční banka & Corporate Clients")
    st.divider()
    
    st.markdown("#### ⚙️ Cloud System Status")
    try:
        health = client.health()
        st.success(f"PerDiemo API: Online (v{health.get('version', '1.0')})")
    except Exception:
        st.warning("PerDiemo API: Cloud Connecting...")

    st.markdown(f"**AWS Region:** `{agent.region_name}`")
    
    # Clean model display name
    model_name = agent.model_id
    if "claude-sonnet-4-5" in model_name:
        model_display = "Claude Sonnet 4.5 (Bedrock)"
    elif "claude-haiku-4-5" in model_name:
        model_display = "Claude Haiku 4.5 (Bedrock)"
    elif "claude-3-5-sonnet" in model_name:
        model_display = "Claude 3.5 Sonnet (Bedrock)"
    else:
        model_display = model_name.split(":")[-2].split(".")[-1] if ":" in model_name else model_name
    st.markdown(f"**Model:** `{model_display}`")
    st.divider()
    st.caption("Evidentiary Audit Standard: NSS 3 Afs 97/2025 - 71")

# Main Header
st.markdown('<div class="main-header">⚖️ PerDiemo Copilot — Autonomous Travel Expense Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated receipt intake, statutory Czech Labour Code per diems, and Komerční banka back-office compliance control.</div>', unsafe_allow_html=True)

col_input, col_audit = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 1. Document & Trip Intake")
    
    intake_mode = st.radio("Intake Source:", ["Sample Preset", "Free-form Text / Slack Log", "Document Upload (PDF/Image)"], horizontal=True)
    
    sample_text = (
        "Departed Prague on June 10, 2025 at 07:00 AM by company car to Vienna for client meetings. "
        "Crossed the border at Mikulov at 09:30 AM, arrived in Vienna at 11:00 AM. "
        "Overnight at Grand Hotel Wien with complimentary breakfast included in room rate. "
        "On June 11 departed Vienna at 16:00, crossed border back into Czechia at 17:30, arrived in Prague at 20:00."
    )
    
    if intake_mode == "Sample Preset":
        trip_text = st.text_area("Trip Description:", value=sample_text, height=120)
    elif intake_mode == "Free-form Text / Slack Log":
        trip_text = st.text_area("Trip Description:", placeholder="Paste Slack messages, email confirmations or notes...", height=120)
    else:
        uploaded_file = st.file_uploader("Upload Boarding Pass or Hotel Receipt:", type=["jpg", "png", "pdf"])
        trip_text = sample_text

    year_select = st.selectbox("Statutory Tax Year:", [2026, 2025, 2024], index=1)
    
    simulate_fraud = st.checkbox("⚠️ Simulate Compliance Anomaly (Hide Hotel Breakfast)", value=False, help="Uncheck declared breakfast to test Komerční banka's meal double-dipping fraud detector.")

    process_btn = st.button("🚀 Run Autonomous Agent & Audit", type="primary", use_container_width=True)

if process_btn or "last_result" in st.session_state:
    if process_btn:
        with st.spinner("🤖 AWS Bedrock Agent parsing travel events..."):
            extracted = agent.extract_from_text(trip_text)
            
            # Allow fraud simulation
            if simulate_fraud:
                extracted["bezplatna_strava"] = {}
                extracted["hotel_info"]["breakfast_included"] = True

        with st.spinner("⚖️ Computing statutory allowances via PerDiemo Cloud Engine..."):
            trips_payload = [{
                "id_cesty": "KB-AUDIT-2025-001",
                "ucel_cesty": extracted.get("ucel_cesty", "Business"),
                "vlastnictvi_vozidla": extracted.get("typ_vozidla", "SLUZEBNI"),
                "zamestnanec_jednatel": extracted.get("zamestnanec_jednatel", "Alex Miller"),
                "spolecnost": extracted.get("spolecnost", "KB Enterprise Client"),
                "bezplatna_strava": extracted.get("bezplatna_strava", {}),
                "itinerar": extracted.get("itinerary", [])
            }]
            calc_result = client.calculate(trips_payload, year=year_select)

        with st.spinner("🛡️ Running Komerční Banka Back-Office Auditor rules..."):
            audit_report = auditor.audit_trip(extracted, calc_result)

        st.session_state["last_result"] = {
            "extracted": extracted,
            "calc": calc_result,
            "audit": audit_report
        }

    # Render Results
    res = st.session_state["last_result"]
    extracted = res["extracted"]
    calc_result = res["calc"]
    audit_report = res["audit"]
    meta = calc_result.get("metadata", {})

    with col_input:
        st.markdown("#### 📋 Extracted Itinerary Breakdown")
        legs = extracted.get("itinerary", [])
        if legs:
            df_legs = pd.DataFrame(legs)[["typ", "datum", "misto", "country_code", "transport_type"]]
            st.dataframe(df_legs, use_container_width=True, hide_index=True)

        st.markdown(f"**Business Purpose:** {extracted.get('ucel_cesty')}")
        st.markdown(f"**Vehicle:** `{extracted.get('typ_vozidla')}` | **Free Meals Declared:** `{extracted.get('bezplatna_strava')}`")

    with col_audit:
        st.markdown("### 2. Komerční Banka Back-Office Audit Verdict")
        
        # Verdict Banner
        verdict = audit_report.get("verdict")
        score = audit_report.get("risk_score", 0)
        
        if verdict == "APPROVED":
            st.success(f"✅ VERDICT: **APPROVED FOR REIMBURSEMENT** (Risk Score: {score}/100)")
        elif verdict == "FLAGGED_FOR_REVIEW":
            st.warning(f"⚠️ VERDICT: **FLAGGED FOR ACCOUNTANT REVIEW** (Risk Score: {score}/100)")
        else:
            st.error(f"❌ VERDICT: **EXPENSE REJECTED** (Risk Score: {score}/100)")

        # Metric Tiles
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Stravné", f"{meta.get('total_stravne_czk', 0):,.2f} CZK")
        m2.metric("Meal Deductions", f"-{meta.get('total_kraceni_czk', 0):,.2f} CZK")
        m3.metric("Pocket Money", f"{meta.get('total_kapesne_czk', 0):,.2f} CZK")

        st.markdown("#### 🔍 Compliance Audit Findings")
        for finding in audit_report.get("findings", []):
            sev = finding.get("severity")
            rule = finding.get("rule")
            msg = finding.get("message")
            
            if sev == "PASSED":
                st.markdown(f'<span class="badge-passed">PASS</span> **{rule}**: {msg}', unsafe_allow_html=True)
            elif sev == "WARNING":
                st.markdown(f'<span class="badge-warning">WARN</span> **{rule}**: {msg}', unsafe_allow_html=True)
            elif sev == "CRITICAL":
                st.markdown(f'<span class="badge-critical">CRITICAL</span> **{rule}**: {msg}', unsafe_allow_html=True)
            else:
                st.markdown(f"ℹ️ **{rule}**: {msg}")

        st.divider()
        st.markdown(f"**🔒 Cryptographic Audit Seal (SHA-256):**")
        st.code(meta.get("verification_signature", "N/A"), language="text")

        st.button("📥 1-Click Approve & Export to Accounting (Pohoda XML)", type="primary", use_container_width=True)
