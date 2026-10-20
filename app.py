# -*- coding: utf-8 -*-
"""
app.py — Interactive Streamlit Dashboard for PerDiemo Copilot.

Designed for The FinTechers Hackathon 2026 (Prague):
- TRACK 01: Agentic Payments & Money Movement (MoroSystems Payments Sandbox & Conversational Ops)
- TRACK 06: Finance Operations & Back-Office AI (Komerční banka Compliance & Statutory Per Diems)
"""
import os
import time
import json
import importlib
import streamlit as st
import pandas as pd

import perdiemo_client
import agent_intake
import backoffice_auditor
import morosystems_client
import document_package_auditor

# Hot reload submodules to bust Streamlit process cache
importlib.reload(perdiemo_client)
importlib.reload(agent_intake)
importlib.reload(backoffice_auditor)
importlib.reload(morosystems_client)
importlib.reload(document_package_auditor)

from perdiemo_client import PerDiemoClient
from agent_intake import BedrockIntakeAgent
from backoffice_auditor import BackOfficeAuditor
from morosystems_client import MoroSystemsPaymentClient
from document_package_auditor import DocumentPackageAuditor

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
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    div[data-testid="stColumn"] button[kind="secondary"] {
        white-space: nowrap !important;
        padding: 0.35rem 0.55rem !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Services (no stale cache across edits)
def get_services():
    client = PerDiemoClient()
    agent = BedrockIntakeAgent()
    auditor = BackOfficeAuditor()
    moro_client = MoroSystemsPaymentClient()
    doc_package_auditor = DocumentPackageAuditor()
    return client, agent, auditor, moro_client, doc_package_auditor

client, agent, auditor, moro_client, doc_package_auditor = get_services()

def apply_remediation(rule_id: str, remediation_type: str, key_prefix: str = "tab1"):
    """
    Executes automated 1-click remediation for compliance anomalies, recalculating
    statutory per diems through the PerDiemo Cloud Engine and issuing an updated SHA-256 seal.
    """
    action_summary = ""

    if key_prefix == "tab1" and "card_settlement" in st.session_state:
        card_settlement = st.session_state["card_settlement"]
        clustered = card_settlement["clustered"]
        stat_itinerary = clustered.get("statutory_itinerary", {})
        tsys_data = st.session_state.get("tsys_data", {})
        tx_list = tsys_data.get("transactions", [])
        oop_list = tsys_data.get("out_of_pocket_cash", [])

        if remediation_type == "apply_meal_deduction":
            dates = set()
            for leg in stat_itinerary.get("itinerary", []):
                d = str(leg.get("datum", ""))[:10]
                if d:
                    dates.add(d)
            if not dates and "detected_trip" in clustered:
                st_date = clustered["detected_trip"].get("start_time", "")[:10]
                if st_date:
                    dates.add(st_date)
            for d in dates:
                stat_itinerary.setdefault("bezplatna_strava", {})[d] = ["snidane"]
            stat_itinerary.setdefault("hotel_info", {})["breakfast_included"] = True
            action_summary = "Applied mandatory statutory meal reduction (70%/25% under § 163 ZP) for breakfast dates."

        elif remediation_type == "confirm_room_only":
            stat_itinerary.setdefault("hotel_info", {})["breakfast_included"] = False
            stat_itinerary["bezplatna_strava"] = {}
            action_summary = "Confirmed Room-Only accommodation without complimentary breakfast; preserved 100% statutory per diem (§§ 163 & 170 ZP)."

        elif remediation_type == "attach_weekend_justification":
            curr_purpose = stat_itinerary.get("ucel_cesty", "Business Negotiations")
            stat_itinerary["ucel_cesty"] = f"{curr_purpose} — [Mandatory Client Meeting & Urgent On-Site Deployment (§ 156 ZP Approved)]"
            action_summary = "Attached statutory business urgency justification for weekend travel legs under § 156 ZP."

        elif remediation_type == "manager_overrule":
            action_summary = "Line manager authorized policy compliance waiver under corporate expense rule exceptions."

        # Re-run Statutory Engine & Auditor
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
        settlement = auditor.reconcile_and_settle(stat_itinerary, calc_result, tx_list, oop_list)

        st.session_state["card_settlement"] = {
            "clustered": clustered,
            "calc": calc_result,
            "settlement": settlement
        }
        st.session_state.pop("payout_receipt", None)

    elif key_prefix == "tab2" and "doc_audit_result" in st.session_state:
        doc_res = st.session_state["doc_audit_result"]
        extracted = doc_res["extracted"]

        if remediation_type == "apply_meal_deduction":
            dates = set()
            for leg in extracted.get("itinerary", []):
                d = str(leg.get("datum", ""))[:10]
                if d:
                    dates.add(d)
            for d in dates:
                extracted.setdefault("bezplatna_strava", {})[d] = ["snidane"]
            extracted.setdefault("hotel_info", {})["breakfast_included"] = True
            extracted["has_breakfast_receipt"] = False
            action_summary = "Applied mandatory statutory meal reduction (70%/25% under § 163 ZP) for breakfast dates and resolved double-dipping alert."

        elif remediation_type == "confirm_room_only":
            extracted.setdefault("hotel_info", {})["breakfast_included"] = False
            extracted["bezplatna_strava"] = {}
            extracted["has_breakfast_receipt"] = False
            action_summary = "Confirmed Room-Only accommodation without complimentary breakfast; preserved 100% statutory per diem."

        elif remediation_type == "attach_weekend_justification":
            curr_purpose = extracted.get("ucel_cesty", "Business Negotiations")
            extracted["ucel_cesty"] = f"{curr_purpose} — [Mandatory Client Meeting & Urgent On-Site Deployment (§ 156 ZP Approved)]"
            action_summary = "Attached statutory business urgency justification for weekend travel legs under § 156 ZP."

        elif remediation_type == "manager_overrule":
            action_summary = "Line manager authorized policy compliance waiver under corporate expense rule exceptions."

        trips_payload = [{
            "id_cesty": "KB-DOC-AUDIT-001",
            "ucel_cesty": extracted.get("ucel_cesty", "Business"),
            "vlastnictvi_vozidla": extracted.get("typ_vozidla", "SLUZEBNI"),
            "zamestnanec_jednatel": extracted.get("zamestnanec_jednatel", "Alex Miller"),
            "spolecnost": extracted.get("spolecnost", "KB Enterprise Client"),
            "bezplatna_strava": extracted.get("bezplatna_strava", {}),
            "itinerar": extracted.get("itinerary", [])
        }]
        calc_result = client.calculate(trips_payload, year=2025)
        audit_report = auditor.audit_trip(extracted, calc_result)

        st.session_state["doc_audit_result"] = {
            "extracted": extracted,
            "calc": calc_result,
            "audit": audit_report
        }
        st.session_state.pop("doc_payout_receipt", None)

    # Record in Copilot chat thread
    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = []
    log_msg = f"⚡ **Manager Remediation Executed for {rule_id}**: {action_summary} Statutory per diems recalculated via PerDiemo cloud engine and sealed with new SHA-256 signature."
    st.session_state["chat_thread"].append({"role": "assistant", "content": log_msg})

@st.dialog("🤖 PerDiemo Copilot — AI Rule Advisory & One-Click Remediation", width="large")
def show_rule_explanation_dialog(finding: dict, trip_context: dict, key_prefix: str = "tab1", dialog_key: str = ""):
    sev = str(finding.get("severity", "INFO")).upper()
    rule = finding.get("rule", "KB-RULE")
    msg = finding.get("message", "")

    st.markdown(f"### 🛡️ `{rule}`")
    render_audit_finding(finding, show_explain=False)

    if sev in ["CRITICAL", "WARNING"]:
        prompt_q = (
            f"Explain how {rule} was evaluated for this trip, why it produced severity '{sev}', "
            f"and what concrete suggestions and remediation steps should be taken to resolve the issue."
        )
    else:
        prompt_q = (
            f"Explain how {rule} was evaluated for this trip, why it produced severity '{sev}', "
            f"and what statutory provisions confirm full compliance."
        )

    st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.08); padding: 0.8rem 1rem; border-radius: 8px; margin: 0.8rem 0; border-left: 4px solid #6366f1;">
            <div style="font-size: 0.72rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.05em;">❓ Question Asked to AI Agent:</div>
            <div style="font-size: 0.92rem; font-style: italic; margin-top: 4px; color: inherit;">"{prompt_q}"</div>
        </div>
    """, unsafe_allow_html=True)

    # Cache AI explanation to prevent expensive re-invocation on dialog button interactions
    cache_key = f"cache_explain_{key_prefix}_{rule}_{sev}"
    if cache_key not in st.session_state:
        with st.spinner("🤖 Bedrock Claude Sonnet 4.5 analyzing statutory rules & formulating advice..."):
            st.session_state[cache_key] = agent.explain_audit_rule(finding, trip_context)
    ai_reply = st.session_state[cache_key]

    st.markdown("#### 🧠 Copilot Audit Assessment & Guidance")
    st.markdown(ai_reply)

    # Automatically save to chat thread so user can continue seamlessly in chat
    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = []

    already_in_chat = any(m.get("content") == prompt_q for m in st.session_state["chat_thread"])
    if not already_in_chat:
        st.session_state["chat_thread"].append({"role": "user", "content": prompt_q})
        st.session_state["chat_thread"].append({"role": "assistant", "content": ai_reply})

    # =========================================================================
    # ⚡ ONE-CLICK REMEDIATION WORKFLOW (MANAGER APPROVAL)
    # =========================================================================
    st.markdown("---")
    if sev in ["CRITICAL", "WARNING"]:
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(245, 158, 11, 0.08) 100%); padding: 1rem 1.2rem; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.3); margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 800; color: #b45309; display: flex; align-items: center; gap: 8px;">
                    <span>⚡</span> <span>Manager Action Workflow: One-Click Remediation</span>
                </div>
                <div style="font-size: 0.84rem; color: #475569; margin-top: 4px;">
                    Save valuable back-office approval time. Click a recommended solution below to automatically adjust statutory declarations, recompute allowances via PerDiemo engine, and generate a new SHA-256 seal.
                </div>
            </div>
        """, unsafe_allow_html=True)

        if "MEAL-DOUBLE-DIPPING" in rule or "RULE-01" in rule:
            c_act1, c_act2 = st.columns(2)
            with c_act1:
                st.markdown("**Option A (Statutory Deduction):**")
                st.caption("Apply statutory meal deduction (70%/25% under § 163 ZP) for breakfast days.")
                if st.button("⚡ Apply Meal Reduction & Recalculate", type="primary", use_container_width=True, key=f"rem_deduct_{rule}_{key_prefix}"):
                    if dialog_key:
                        st.session_state[dialog_key] = False
                    st.session_state.pop(cache_key, None)
                    apply_remediation(rule, "apply_meal_deduction", key_prefix)
                    st.toast("🎉 Applied meal deduction (-70%/25%)! Recalculated & Re-sealed.", icon="⚡")
                    st.rerun()
            with c_act2:
                st.markdown("**Option B (Folio Verification):**")
                st.caption("Confirm hotel booking was Room-Only; waive breakfast deduction.")
                if st.button("📄 Confirm Room-Only Folio (Preserve 100%)", use_container_width=True, key=f"rem_room_{rule}_{key_prefix}"):
                    if dialog_key:
                        st.session_state[dialog_key] = False
                    st.session_state.pop(cache_key, None)
                    apply_remediation(rule, "confirm_room_only", key_prefix)
                    st.toast("🎉 Room-only confirmed! 100% per diem preserved & Re-sealed.", icon="📄")
                    st.rerun()

        elif "WEEKEND-TRAVEL" in rule or "RULE-02" in rule:
            st.markdown("**Recommended Remediation:**")
            st.caption("Attach documented business urgency justification to satisfy Czech tax authorities (§ 156 ZP).")
            c_wk1, c_wk2 = st.columns([1.5, 1])
            with c_wk1:
                if st.button("⚡ Auto-Attach Business Justification & Approve", type="primary", use_container_width=True, key=f"rem_wknd_{rule}_{key_prefix}"):
                    if dialog_key:
                        st.session_state[dialog_key] = False
                    st.session_state.pop(cache_key, None)
                    apply_remediation(rule, "attach_weekend_justification", key_prefix)
                    st.toast("🎉 Justification attached! Warning cleared & Re-sealed.", icon="⚡")
                    st.rerun()
            with c_wk2:
                if st.button("👔 Approve with Manager Discretion", use_container_width=True, key=f"rem_wknd_mgr_{rule}_{key_prefix}"):
                    if dialog_key:
                        st.session_state[dialog_key] = False
                    st.session_state.pop(cache_key, None)
                    apply_remediation(rule, "manager_overrule", key_prefix)
                    st.toast("🎉 Manager approval recorded!", icon="👔")
                    st.rerun()

        elif "AUDIT-FINGERPRINT" in rule or "RULE-03" in rule:
            st.markdown("**Recommended Remediation:**")
            st.caption("Re-run the calculation through the PerDiemo Cloud Engine to generate a verified 64-char SHA-256 seal.")
            if st.button("🔒 Re-Calculate & Generate Cryptographic Seal", type="primary", use_container_width=True, key=f"rem_seal_{rule}_{key_prefix}"):
                if dialog_key:
                    st.session_state[dialog_key] = False
                st.session_state.pop(cache_key, None)
                apply_remediation(rule, "recalculate_seal", key_prefix)
                st.toast("🎉 Fresh SHA-256 seal generated!", icon="🔒")
                st.rerun()

        else:
            st.markdown("**Recommended Remediation:**")
            st.caption("Authorize policy exception under approving line-manager authority.")
            if st.button("👔 Fast-Track Manager Approval & Record Memo", type="primary", use_container_width=True, key=f"rem_gen_{rule}_{key_prefix}"):
                if dialog_key:
                    st.session_state[dialog_key] = False
                st.session_state.pop(cache_key, None)
                apply_remediation(rule, "manager_overrule", key_prefix)
                st.toast("🎉 Manager approval recorded!", icon="👔")
                st.rerun()

    else:
        st.markdown("""
            <div style="background: rgba(34, 197, 94, 0.08); padding: 0.9rem 1.1rem; border-radius: 8px; border: 1px solid rgba(34, 197, 94, 0.25);">
                <div style="font-weight: 700; color: #166534; display: flex; align-items: center; gap: 6px;">
                    <span>✅</span> <span>Fully Compliant — No Manager Action Required</span>
                </div>
                <div style="font-size: 0.84rem; color: #475569; margin-top: 3px;">
                    This expense leg satisfies Czech Labour Code (§§ 151–189 ZP) statutory criteria and Komerční banka compliance policies.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Optional action for Tab 1 to test applying meal deduction even if room-only
        if "MEAL-DOUBLE-DIPPING" in rule or "RULE-01" in rule:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.caption("💡 *Manager Option: If an itemized folio later reveals complimentary breakfast was consumed, you can apply the statutory reduction here:*")
            if st.button("⚡ Apply Statutory Breakfast Reduction (-70%/25%)", use_container_width=False, key=f"rem_opt_deduct_{rule}_{key_prefix}"):
                if dialog_key:
                    st.session_state[dialog_key] = False
                st.session_state.pop(cache_key, None)
                apply_remediation(rule, "apply_meal_deduction", key_prefix)
                st.toast("Applied meal reduction & re-calculated!", icon="⚡")
                st.rerun()

    st.divider()
    c_btn1, c_btn2 = st.columns([1.2, 0.8])
    with c_btn1:
        st.caption("💬 Q&A and manager actions are automatically recorded in your **Copilot Chat Thread** below.")
    with c_btn2:
        if st.button("✖️ Close Dialog", use_container_width=True, key=f"dlg_close_{rule}_{key_prefix}"):
            if dialog_key:
                st.session_state[dialog_key] = False
            st.rerun()

def render_audit_finding(finding, idx=0, show_explain=True, trip_context=None, key_prefix="t1"):
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

    card_html = f"""
        <div class="finding-item {cls}">
            <div style="flex-shrink: 0; margin-top: 1px;">{badge}</div>
            <div style="flex-grow: 1;">
                <span class="rule-tag">{rule}</span> &nbsp;{msg}
            </div>
        </div>
    """

    if show_explain:
        col_card, col_btn = st.columns([3.3, 1.2])
        with col_card:
            st.markdown(card_html, unsafe_allow_html=True)
        with col_btn:
            dlg_key = f"dlg_active_{key_prefix}_{rule}_{idx}"
            if st.button("Explain", icon=":material/lightbulb:", key=f"btn_explain_{key_prefix}_{rule}_{idx}", use_container_width=True, help=f"Ask AI Agent to explain {rule} and suggest actions"):
                st.session_state[dlg_key] = True

            if st.session_state.get(dlg_key, False):
                show_rule_explanation_dialog(finding, trip_context or {}, key_prefix=key_prefix, dialog_key=dlg_key)
    else:
        st.markdown(card_html, unsafe_allow_html=True)

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
            with st.expander("🔍 View Compliance Audit Findings & Cryptographic Seal", expanded=True):
                trip_ctx = {
                    "destination": dest_choice if "dest_choice" in locals() else "Vienna",
                    "tsys_data": tsys_data,
                    "card_settlement": st.session_state.get("card_settlement")
                }
                for idx, f in enumerate(settlement.get("findings", [])):
                    render_audit_finding(f, idx=idx, show_explain=True, trip_context=trip_ctx, key_prefix="tab1")
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
            files_to_process = None
        elif intake_mode == "Free-form Text / Slack Log":
            trip_text = st.text_area("Trip Description:", placeholder="Paste Slack messages...", height=120, key="doc_free_area")
            files_to_process = None
        else:
            st.markdown("##### 📎 Upload Receipts & Travel Documents (PDF / Images)")
            uploaded_files = st.file_uploader(
                "Upload boarding passes, hotel folios, taxi or restaurant receipts:",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="doc_multi_uploader"
            )

            st.markdown('<div style="font-size: 0.85rem; font-weight: 600; color: #475569; margin-top: 0.4rem;">Or load pre-bundled synthetic test scenarios:</div>', unsafe_allow_html=True)
            scen_col1, scen_col2, scen_col3 = st.columns(3)
            with scen_col1:
                if st.button("📁 Clean Trip", help="Loads flight boarding passes, hotel folio, taxi, and dinner receipts.", use_container_width=True, key="btn_scen_clean"):
                    st.session_state["selected_demo_scenario"] = "clean"
            with scen_col2:
                if st.button("🚨 Double-Dipping", help="Loads Hotel Folio with breakfast + separate breakfast receipt to trigger fraud.", use_container_width=True, key="btn_scen_fraud"):
                    st.session_state["selected_demo_scenario"] = "fraud"
            with scen_col3:
                if st.button("🏖️ Weekend Trip", help="Loads suspicious weekend hotel stay without documented urgency.", use_container_width=True, key="btn_scen_weekend"):
                    st.session_state["selected_demo_scenario"] = "weekend"

            demo_dir = os.path.join(os.path.dirname(__file__), "demo_documents")
            files_to_process = []

            # Prioritize uploaded files if any
            if uploaded_files:
                st.session_state.pop("selected_demo_scenario", None)
                for uf in uploaded_files:
                    b = uf.read()
                    files_to_process.append({
                        "name": uf.name,
                        "bytes": b,
                        "size": len(b)
                    })
                    uf.seek(0)
            elif st.session_state.get("selected_demo_scenario"):
                scen = st.session_state["selected_demo_scenario"]
                preset_filenames = []
                if scen == "clean":
                    preset_filenames = [
                        "boarding_pass_PRG_VIE.pdf",
                        "hotel_folio_grand_wien.pdf",
                        "taxi_receipt_airport.pdf",
                        "restaurant_receipt_dinner.pdf",
                        "boarding_pass_VIE_PRG.pdf"
                    ]
                    st.info("ℹ️ Loaded **Clean Business Trip Scenario** (5 synthetic PDFs).")
                elif scen == "fraud":
                    preset_filenames = [
                        "hotel_folio_grand_wien.pdf",
                        "breakfast_receipt_fraud.pdf"
                    ]
                    st.error("🚨 Loaded **Meal Double-Dipping Fraud Scenario** (Hotel with Breakfast + Separate Breakfast Receipt).")
                elif scen == "weekend":
                    preset_filenames = [
                        "hotel_weekend_suspicious.pdf"
                    ]
                    st.warning("⚠️ Loaded **Weekend Travel Anomaly Scenario** (Saturday/Sunday trip leg).")

                for fn in preset_filenames:
                    fp = os.path.join(demo_dir, fn)
                    if os.path.exists(fp):
                        with open(fp, "rb") as f:
                            content = f.read()
                            files_to_process.append({
                                "name": fn,
                                "bytes": content,
                                "size": len(content)
                            })

            if files_to_process:
                st.markdown(f"**{len(files_to_process)} document(s) ready for autonomous audit:**")
                for f_item in files_to_process:
                    fn = f_item["name"]
                    sz_kb = f_item["size"] / 1024
                    icon = "🏨" if "hotel" in fn.lower() else ("✈️" if "boarding" in fn.lower() or "pass" in fn.lower() else ("🍳" if "breakfast" in fn.lower() else ("🚕" if "taxi" in fn.lower() else "🧾")))
                    st.markdown(f"- {icon} `{fn}` ({sz_kb:.1f} KB)")
            trip_text = sample_text

        year_select = st.selectbox("Statutory Tax Year:", [2026, 2025, 2024], index=1, key="doc_year")
        simulate_fraud = st.checkbox("⚠️ Simulate Compliance Anomaly (Hide Hotel Breakfast)", value=False, help="Uncheck declared breakfast to test Komerční banka's meal double-dipping fraud detector.", key="doc_fraud")
        process_doc_btn = st.button("🚀 Run Autonomous Document Audit", type="primary", use_container_width=True, key="doc_proc_btn")

    with col_audit_doc:
        st.markdown("### 2. Komerční Banka Audit Protocol")
        if process_doc_btn or "doc_audit_result" in st.session_state:
            if process_doc_btn:
                st.session_state.pop("doc_payout_receipt", None)

                if intake_mode == "Document Upload (PDF/Image)":
                    if not files_to_process:
                        st.warning("Please upload receipts or select a demo scenario above.")
                        st.stop()

                    extractions = []
                    combined_itinerary = []
                    combined_meals = {}
                    hotel_data = {}
                    traveler_name = None
                    trip_purpose = None
                    has_breakfast_receipt = False
                    any_hotel_has_breakfast = False
                    docs_for_pkg = []

                    with st.spinner(f"🤖 Processing {len(files_to_process)} document(s) with Bedrock Multimodal Vision..."):
                        for f_info in files_to_process:
                            f_name = f_info["name"]
                            f_bytes = f_info["bytes"]

                            # Extract text for package auditor
                            doc_text = ""
                            if f_name.lower().endswith(".pdf"):
                                try:
                                    from pypdf import PdfReader
                                    reader = PdfReader(io.BytesIO(f_bytes))
                                    for page in reader.pages[:5]:
                                        doc_text += (page.extract_text() or "") + "\n"
                                except Exception:
                                    doc_text = ""

                            try:
                                extraction = agent.extract_from_file(f_bytes, f_name)
                            except Exception as e:
                                extraction = {"error": str(e)}

                            extractions.append({
                                "filename": f_name,
                                "size": f_info["size"],
                                "data": extraction
                            })

                            docs_for_pkg.append({
                                "filename": f_name,
                                "text": doc_text,
                                "extracted_data": extraction
                            })

                            if extraction and not extraction.get("error"):
                                if extraction.get("itinerary"):
                                    combined_itinerary.extend(extraction["itinerary"])
                                if extraction.get("bezplatna_strava"):
                                    combined_meals.update(extraction["bezplatna_strava"])
                                if extraction.get("hotel_info", {}).get("hotel_name"):
                                    hotel_data = extraction["hotel_info"]
                                    if extraction["hotel_info"].get("breakfast_included"):
                                        any_hotel_has_breakfast = True
                                if extraction.get("zamestnanec_jednatel") and not traveler_name:
                                    traveler_name = extraction["zamestnanec_jednatel"]
                                if extraction.get("ucel_cesty") and not trip_purpose:
                                    trip_purpose = extraction["ucel_cesty"]

                                doc_type = extraction.get("document_type", "")
                                meal_info = extraction.get("meal_receipt", {})
                                if doc_type == "meal_receipt" and meal_info.get("meal_type") == "breakfast":
                                    has_breakfast_receipt = True

                    # Run Package Auditor
                    pkg_audit_res = doc_package_auditor.audit_package(docs_for_pkg)

                    if any_hotel_has_breakfast:
                        if not hotel_data:
                            hotel_data = {"hotel_name": "Grand Hotel Wien", "breakfast_included": True}
                        else:
                            hotel_data["breakfast_included"] = True

                    # Sort itinerary
                    combined_itinerary = sorted(combined_itinerary, key=lambda x: str(x.get("datum", "")))

                    extracted = {
                        "ucel_cesty": trip_purpose or "Client Negotiations & Business Travel",
                        "typ_vozidla": "SLUZEBNI",
                        "zamestnanec_jednatel": traveler_name or "Alex Miller",
                        "spolecnost": "KB Enterprise Client",
                        "itinerary": combined_itinerary,
                        "bezplatna_strava": combined_meals,
                        "hotel_info": hotel_data,
                        "has_breakfast_receipt": has_breakfast_receipt
                    }

                    if simulate_fraud:
                        extracted["bezplatna_strava"] = {}
                        extracted["hotel_info"]["breakfast_included"] = True

                else:
                    with st.spinner("🤖 Bedrock Agent extracting structured statutory itinerary..."):
                        extracted = agent.extract_from_text(trip_text)
                        if simulate_fraud:
                            extracted["bezplatna_strava"] = {}
                            extracted["hotel_info"]["breakfast_included"] = True
                    extractions = None
                    pkg_audit_res = None

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
                    "audit": audit_report,
                    "file_extractions": extractions,
                    "pkg_audit": pkg_audit_res
                }

            doc_res = st.session_state["doc_audit_result"]
            extracted = doc_res.get("extracted", {})
            audit_report = doc_res["audit"]
            meta = doc_res["calc"].get("metadata", {})

            # Document Package Audit summary if files were processed
            pkg_res = doc_res.get("pkg_audit")
            if pkg_res:
                col_pk1, col_pk2 = st.columns([1, 2])
                with col_pk1:
                    st.metric("Package Completeness", f"{pkg_res.completeness_score:.0f}%")
                with col_pk2:
                    if pkg_res.missing_documents:
                        st.caption(f"⚠️ Missing: {', '.join(pkg_res.missing_documents)}")
                    else:
                        st.caption("✅ All essential travel supporting documents present.")

            file_exts = doc_res.get("file_extractions")
            if file_exts:
                with st.expander(f"📄 View Extracted Document Intelligence ({len(file_exts)} documents)", expanded=False):
                    for item in file_exts:
                        d_name = item["filename"]
                        d_data = item.get("data", {})
                        d_type = d_data.get("document_type", "document")
                        st.markdown(f"**`{d_name}`** — Type: `{d_type}`")
                        if d_data.get("hotel_info", {}).get("hotel_name"):
                            h_name = d_data["hotel_info"]["hotel_name"]
                            b_inc = d_data["hotel_info"].get("breakfast_included")
                            st.write(f"- Hotel: **{h_name}** (Breakfast: {'Included' if b_inc else 'Room Only'})")
                        if d_data.get("meal_receipt", {}).get("meal_type"):
                            m_type = d_data["meal_receipt"]["meal_type"]
                            m_amt = d_data["meal_receipt"].get("amount")
                            m_curr = d_data["meal_receipt"].get("currency", "EUR")
                            st.write(f"- Meal Receipt: **{m_type.capitalize()}** ({m_amt} {m_curr})")
                        if d_data.get("itinerary"):
                            st.write(f"- Itinerary Legs: {len(d_data['itinerary'])} detected")
                        st.divider()

            verdict = audit_report.get("verdict")
            score = audit_report.get("risk_score", 0)
            if verdict == "APPROVED":
                st.success(f"✅ VERDICT: **APPROVED FOR REIMBURSEMENT** (Risk Score: {score}/100)")
            elif verdict == "FLAGGED_FOR_REVIEW":
                st.warning(f"⚠️ VERDICT: **FLAGGED FOR ACCOUNTANT REVIEW** (Risk Score: {score}/100)")
            else:
                st.error(f"❌ VERDICT: **EXPENSE REJECTED** (Risk Score: {score}/100)")

            # Statutory metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Net Stravné", f"{meta.get('total_stravne_czk', 0):,.2f} CZK")
            m2.metric("Meal Deductions", f"-{meta.get('total_kraceni_czk', 0):,.2f} CZK")
            m3.metric("Pocket Money", f"{meta.get('total_kapesne_czk', 0):,.2f} CZK")

            # Calculate Net Reimbursement for Tab 2
            total_stravne = float(meta.get("total_stravne_czk", 0.0) or 0.0)
            total_kapesne = float(meta.get("total_kapesne_czk", 0.0) or 0.0)
            total_nahrada = float(meta.get("total_nahrada_vozidlo_czk", 0.0) or 0.0)
            doc_payout_amount = round(total_stravne + total_kapesne + total_nahrada, 2)
            employee_name = extracted.get("zamestnanec_jednatel", "Alex Miller")
            employee_iban = "CZ6501000000001928374650"
            employee_id = "EMP-KB-0042"

            trip_dest = "Business Trip"
            for leg in extracted.get("itinerary", []):
                if leg.get("typ") in ["PRIJEZD", "LAYOVER"] or (leg.get("country_code") and leg.get("country_code") != "CZE"):
                    trip_dest = leg.get("misto", "Business Trip")
                    break
            trip_ref = f"{trip_dest} Reimbursement ({extracted.get('ucel_cesty', 'Travel Claim')[:20]})"

            # Net Settlement Card (Manager Overview)
            st.markdown(f"""
                <div class="settlement-card">
                    <div style="font-size: 0.85rem; color: #166534; font-weight: 700; text-transform: uppercase;">
                        Net Employee Reimbursement Calculated
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 4px 0;">
                        {doc_payout_amount:,.2f} CZK
                    </div>
                    <div style="font-size: 0.85rem; color: #334155;">
                        Target IBAN: <code>{employee_iban}</code> ({employee_name})
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Audit findings
            with st.expander("🔍 View Compliance Audit Findings & Cryptographic Seal", expanded=True):
                doc_trip_ctx = {
                    "extracted_itinerary": extracted,
                    "audit_report": audit_report,
                    "metadata": meta
                }
                for idx, finding in enumerate(audit_report.get("findings", [])):
                    render_audit_finding(finding, idx=idx, show_explain=True, trip_context=doc_trip_ctx, key_prefix="tab2")

                sig = meta.get("verification_signature", "N/A")
                if sig and sig != "N/A":
                    st.markdown('<div style="font-size: 0.78rem; font-weight: 700; color: #64748b; margin-top: 0.9rem; text-transform: uppercase;">🔒 Cryptographic Evidentiary Audit Seal (SHA-256):</div>', unsafe_allow_html=True)
                    st.code(sig, language="text")

            # MoroSystems Execution Gate (Manager Persona)
            st.markdown("#### 🚀 MoroSystems Payments Sandbox Execution")
            st.caption("Track 06 Guardrail: The manager persona authorizes instant payment transfer based on statutory compliance checks.")

            if verdict == "APPROVED":
                if st.button(
                    f"💸 Authorize Instant Payout of {doc_payout_amount:,.2f} CZK via MoroSystems Rail",
                    type="primary",
                    use_container_width=True,
                    key="tab2_moro_payout_approved"
                ):
                    with st.spinner("Executing payment order on MoroSystems sandbox..."):
                        payout_resp = moro_client.execute_payout(
                            recipient_name=employee_name,
                            recipient_iban=employee_iban,
                            amount=doc_payout_amount,
                            currency="CZK",
                            traveler_id=employee_id,
                            trip_reference=trip_ref,
                            explanation_log={
                                "source": "Document Compliance Audit (Track 06)",
                                "verdict": verdict,
                                "risk_score": score,
                                "statutory_stravne_czk": total_stravne,
                                "statutory_kapesne_czk": total_kapesne,
                                "audit_findings": [f.get("rule") for f in audit_report.get("findings", [])]
                            },
                            audit_seal=meta.get("verification_signature", "MOCK-SEAL")
                        )
                        st.session_state["doc_payout_receipt"] = payout_resp

            elif verdict == "FLAGGED_FOR_REVIEW":
                st.warning(
                    f"⚠️ **Manager Review Gate:** This claim was flagged with Risk Score **{score}/100**. "
                    "You may resolve issues with the **💡 Explain** buttons above, or authorize payout with manager sign-off."
                )
                if st.button(
                    f"👔 Manager Sign-Off & Authorize Payout of {doc_payout_amount:,.2f} CZK via MoroSystems Rail",
                    type="primary",
                    use_container_width=True,
                    key="tab2_moro_payout_flagged"
                ):
                    with st.spinner("Executing payment order on MoroSystems sandbox with manager approval sign-off..."):
                        payout_resp = moro_client.execute_payout(
                            recipient_name=employee_name,
                            recipient_iban=employee_iban,
                            amount=doc_payout_amount,
                            currency="CZK",
                            traveler_id=employee_id,
                            trip_reference=trip_ref,
                            explanation_log={
                                "source": "Document Compliance Audit (Track 06)",
                                "verdict": verdict,
                                "risk_score": score,
                                "manager_override": True,
                                "approval_note": "Approved by line manager under corporate expense discretion policy.",
                                "statutory_stravne_czk": total_stravne,
                                "statutory_kapesne_czk": total_kapesne
                            },
                            audit_seal=meta.get("verification_signature", "MOCK-SEAL")
                        )
                        st.session_state["doc_payout_receipt"] = payout_resp

            else:  # REJECTED
                st.error(
                    f"🚫 **Instant Payout Blocked:** Expense claim is **REJECTED** (Risk Score **{score}/100**) "
                    "due to critical statutory or evidentiary violations. Instant payment cannot be dispatched. "
                    "Please click **💡 Explain** on the flagged rules above to apply 1-click remediation before approving."
                )
                st.button(
                    f"🚫 Payout Blocked (Risk Score {score}/100 — Resolve Violations Above)",
                    disabled=True,
                    use_container_width=True,
                    key="tab2_moro_payout_blocked"
                )

            # Display Payment Receipt
            if "doc_payout_receipt" in st.session_state:
                receipt = st.session_state["doc_payout_receipt"]
                st.success(f"🎉 **PAYMENT SETTLED!** {receipt.get('message')}")
                r_col1, r_col2 = st.columns(2)
                r_col1.markdown(f"**Payment ID:** `{receipt.get('payment_id')}`")
                r_col1.markdown(f"**Clearing System:** `{receipt.get('clearing_system')}`")
                r_col2.markdown(f"**Settled At:** `{receipt.get('settled_at')}`")
                r_col2.markdown(f"**Verification Hash:** `{receipt.get('transfer_verification_hash')[:16]}...`")

            # Pohoda XML Export Protocol
            with st.expander("📥 Export Protocol to Pohoda XML / Accounting Ledger", expanded=False):
                st.caption("Generate tax-compliant XML protocol for import into Pohoda, SAP, or Helios accounting systems.")
                pohoda_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<dat:dataPack xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd"
             xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd"
             version="2.0" id="PD-{meta.get('verification_signature', '')[:12]}">
  <dat:dataPackItem id="TRIP-DOC-01" version="2.0">
    <inv:invoice version="2.0">
      <inv:invoiceHeader>
        <inv:invoiceType>receivable</inv:invoiceType>
        <inv:text>Cestovní náhrady — {trip_ref}</inv:text>
        <inv:partnerIdentity>
          <inv:name>{employee_name}</inv:name>
          <inv:accountNumber>{employee_iban}</inv:accountNumber>
        </inv:partnerIdentity>
        <inv:date>{time.strftime('%Y-%m-%d')}</inv:date>
      </inv:invoiceHeader>
      <inv:invoiceDetail>
        <inv:invoiceItem>
          <inv:text>Zákonné stravné a kapesné (§§ 151-189 ZP)</inv:text>
          <inv:quantity>1</inv:quantity>
          <inv:homeCurrency>
            <inv:unitPrice>{doc_payout_amount}</inv:unitPrice>
            <inv:price>{doc_payout_amount}</inv:price>
          </inv:homeCurrency>
          <inv:note>Evidentiary SHA-256: {meta.get('verification_signature', '')}</inv:note>
        </inv:invoiceItem>
      </inv:invoiceDetail>
    </inv:invoice>
  </dat:dataPackItem>
</dat:dataPack>"""
                st.download_button(
                    label="📥 Download Pohoda XML Protocol",
                    data=pohoda_xml,
                    file_name=f"pohoda_travel_claim_{meta.get('verification_signature', '')[:8]}.xml",
                    mime="application/xml",
                    use_container_width=True,
                    key="pohoda_download_tab2"
                )

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
