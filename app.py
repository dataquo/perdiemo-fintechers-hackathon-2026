# -*- coding: utf-8 -*-
"""
app.py — PerDiemo: KB Back-Office Document Control
The FinTechers Hackathon 2026 — Track 06: Finance Operations & Back-Office AI
Komerční banka Challenge: Automating Back-Office Document Controls
"""
import json
import base64
import streamlit as st
import pandas as pd
from datetime import datetime
from perdiemo_client import PerDiemoClient
from agent_intake import BedrockIntakeAgent
from backoffice_auditor import BackOfficeAuditor

# Page config
st.set_page_config(
    page_title="PerDiemo — KB Back-Office AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .block-container { padding-top: 2rem; max-width: 1400px; }

    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    .doc-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .doc-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59,130,246,0.15);
    }

    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }

    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-success { background: #dcfce7; color: #166534; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-error { background: #fee2e2; color: #991b1b; }
    .badge-info { background: #dbeafe; color: #1e40af; }

    .verdict-approved {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }

    .verdict-flagged {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }

    .verdict-rejected {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }

    .finding-item {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }

    .finding-pass { background: #f0fdf4; border-color: #22c55e; }
    .finding-warn { background: #fffbeb; border-color: #f59e0b; }
    .finding-critical { background: #fef2f2; border-color: #ef4444; }

    .pdf-preview {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .extraction-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
    }

    .extraction-icon { font-size: 1.25rem; margin-right: 0.75rem; }
    .extraction-label { color: #64748b; font-size: 0.85rem; min-width: 100px; }
    .extraction-value { color: #1e293b; font-weight: 500; }

    .step-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }

    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #3b82f6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 0.75rem;
    }

    .step-title { font-weight: 600; color: #1e293b; }

    .seal-box {
        background: #1e293b;
        color: #94a3b8;
        font-family: monospace;
        font-size: 0.8rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    return PerDiemoClient(), BedrockIntakeAgent(), BackOfficeAuditor()

client, agent, auditor = init_services()

# Helper function to display PDF preview
def display_pdf_preview(file_bytes, filename):
    """Display a PDF file preview."""
    b64 = base64.b64encode(file_bytes).decode()
    pdf_display = f'''
    <div class="pdf-preview">
        <iframe src="data:application/pdf;base64,{b64}" width="100%" height="200" type="application/pdf"></iframe>
    </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

def display_image_preview(file_bytes, filename):
    """Display an image preview."""
    b64 = base64.b64encode(file_bytes).decode()
    ext = filename.lower().split('.')[-1]
    mime = f"image/{ext}" if ext != 'jpg' else 'image/jpeg'
    st.image(file_bytes, width=200)

# Header
st.markdown('<div class="main-title">⚖️ PerDiemo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Travel Expense Processing & Compliance Audit — Komerční banka Back-Office AI</div>', unsafe_allow_html=True)

# Create tabs for different views
tab_upload, tab_text, tab_about = st.tabs(["📤 Upload Receipts", "💬 Natural Language", "ℹ️ About"])

with tab_upload:
    col_upload, col_results = st.columns([2, 3], gap="large")

    with col_upload:
        st.markdown('<div class="section-header">📎 Upload Travel Receipts</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Drop receipts here",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="file_uploader"
        )

        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} document(s) ready**")

            # Show previews
            for uf in uploaded_files:
                with st.container():
                    file_bytes = uf.read()
                    uf.seek(0)  # Reset for later processing

                    col_preview, col_info = st.columns([1, 2])
                    with col_preview:
                        if uf.name.lower().endswith('.pdf'):
                            st.markdown(f"📄 **{uf.name}**")
                        else:
                            st.image(file_bytes, width=100)

                    with col_info:
                        if not uf.name.lower().endswith('.pdf'):
                            st.markdown(f"**{uf.name}**")
                        st.caption(f"{uf.size / 1024:.1f} KB")

                    st.markdown("---")
        else:
            st.markdown("""
            <div class="doc-card">
                <div style="text-align: center; padding: 2rem; color: #64748b;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                    <div style="font-weight: 500;">Drop your travel receipts here</div>
                    <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                        Boarding passes, hotel folios, taxi receipts, meal receipts
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Demo files available:** `demo_documents/`")

        st.markdown('<div class="section-header">⚙️ Options</div>', unsafe_allow_html=True)

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            year = st.selectbox("Tax Year", [2025, 2026], index=0)
        with col_opt2:
            currency = st.selectbox("Display", ["CZK", "EUR"], index=0)

        process_btn = st.button(
            "🚀 Process Documents",
            type="primary",
            use_container_width=True,
            disabled=not uploaded_files
        )

    with col_results:
        if process_btn and uploaded_files:

            # Initialize result containers
            results_container = st.container()

            with results_container:
                # Step 1: Document Processing
                st.markdown("""
                <div class="step-indicator">
                    <div class="step-number">1</div>
                    <div class="step-title">Extracting Document Data</div>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                status_text = st.empty()

                extractions = []
                combined_itinerary = []
                combined_meals = {}
                hotel_data = {}
                traveler_name = None
                trip_purpose = None
                has_breakfast_receipt = False

                for i, uf in enumerate(uploaded_files):
                    status_text.text(f"Analyzing: {uf.name}")
                    progress_bar.progress((i + 1) / len(uploaded_files))

                    file_bytes = uf.read()

                    try:
                        extraction = agent.extract_from_file(file_bytes, uf.name)
                    except Exception as e:
                        extraction = {"error": str(e)}

                    extractions.append({
                        "filename": uf.name,
                        "size": len(file_bytes),
                        "data": extraction
                    })

                    # Merge extracted data
                    if extraction and not extraction.get("error"):
                        if extraction.get("itinerary"):
                            combined_itinerary.extend(extraction["itinerary"])

                        if extraction.get("bezplatna_strava"):
                            combined_meals.update(extraction["bezplatna_strava"])

                        if extraction.get("hotel_info", {}).get("hotel_name"):
                            hotel_data = extraction["hotel_info"]

                        if extraction.get("zamestnanec_jednatel") and not traveler_name:
                            traveler_name = extraction["zamestnanec_jednatel"]

                        if extraction.get("ucel_cesty") and not trip_purpose:
                            trip_purpose = extraction["ucel_cesty"]

                        # Detect breakfast receipts (for fraud detection)
                        doc_text = str(extraction).lower()
                        filename_lower = uf.name.lower()
                        if ("breakfast" in doc_text or "fruhstuck" in doc_text or
                            "snidane" in doc_text or "breakfast" in filename_lower):
                            if "hotel" not in filename_lower and not extraction.get("hotel_info", {}).get("hotel_name"):
                                has_breakfast_receipt = True

                progress_bar.empty()
                status_text.empty()

                # Sort itinerary
                combined_itinerary = sorted(combined_itinerary, key=lambda x: x.get("datum", ""))

                # Display extraction results
                st.markdown("**Extracted from documents:**")

                for ext in extractions:
                    data = ext.get("data", {})
                    filename = ext["filename"]

                    with st.expander(f"📄 {filename}", expanded=False):
                        if data.get("error"):
                            st.error(f"Extraction error: {data['error']}")
                            continue

                        if data.get("hotel_info", {}).get("hotel_name"):
                            h = data["hotel_info"]
                            st.markdown(f"""
                            <div class="extraction-item">
                                <span class="extraction-icon">🏨</span>
                                <span class="extraction-label">Hotel</span>
                                <span class="extraction-value">{h.get('hotel_name', 'N/A')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            breakfast = h.get("breakfast_included")
                            breakfast_text = "✅ Included" if breakfast else "❌ Not included"
                            st.markdown(f"""
                            <div class="extraction-item">
                                <span class="extraction-icon">🍳</span>
                                <span class="extraction-label">Breakfast</span>
                                <span class="extraction-value">{breakfast_text}</span>
                            </div>
                            """, unsafe_allow_html=True)

                        if data.get("ucel_cesty"):
                            st.markdown(f"""
                            <div class="extraction-item">
                                <span class="extraction-icon">🎯</span>
                                <span class="extraction-label">Purpose</span>
                                <span class="extraction-value">{data['ucel_cesty']}</span>
                            </div>
                            """, unsafe_allow_html=True)

                        if data.get("itinerary"):
                            st.markdown("**Itinerary:**")
                            for leg in data["itinerary"][:4]:
                                st.markdown(f"• `{leg.get('typ')}` {leg.get('datum', '')} — {leg.get('misto', '')} ({leg.get('country_code', '')})")

                        if data.get("bezplatna_strava"):
                            st.markdown("**Free meals declared:**")
                            for date, meals in data["bezplatna_strava"].items():
                                st.markdown(f"• {date}: {', '.join(meals)}")

                st.markdown("---")

                # Step 2: Per Diem Calculation
                st.markdown("""
                <div class="step-indicator">
                    <div class="step-number">2</div>
                    <div class="step-title">Computing Statutory Per Diems</div>
                </div>
                """, unsafe_allow_html=True)

                calc_result = {}
                with st.spinner("Calling PerDiemo Statutory Engine..."):
                    try:
                        trip_payload = [{
                            "id_cesty": f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "ucel_cesty": trip_purpose or "Business Trip",
                            "vlastnictvi_vozidla": "SLUZEBNI",
                            "zamestnanec_jednatel": traveler_name or "Employee",
                            "spolecnost": "KB Enterprise Client",
                            "bezplatna_strava": combined_meals,
                            "itinerar": combined_itinerary
                        }]

                        calc_result = client.calculate(trip_payload, year=year)
                        meta = calc_result.get("metadata", {})
                    except Exception as e:
                        st.error(f"Calculation error: {e}")
                        meta = {}

                # Display metrics
                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{meta.get('total_stravne_czk', 0):,.0f}</div>
                        <div class="metric-label">Per Diem (CZK)</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">-{meta.get('total_kraceni_czk', 0):,.0f}</div>
                        <div class="metric-label">Meal Deductions</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{meta.get('total_kapesne_czk', 0):,.0f}</div>
                        <div class="metric-label">Pocket Money</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Step 3: Compliance Audit
                st.markdown("""
                <div class="step-indicator">
                    <div class="step-number">3</div>
                    <div class="step-title">Compliance Audit</div>
                </div>
                """, unsafe_allow_html=True)

                merged_data = {
                    "ucel_cesty": trip_purpose,
                    "hotel_info": hotel_data,
                    "bezplatna_strava": combined_meals,
                    "itinerary": combined_itinerary,
                    "has_breakfast_receipt": has_breakfast_receipt
                }

                audit_result = auditor.audit_trip(merged_data, calc_result)
                verdict = audit_result.get("verdict", "UNKNOWN")
                risk_score = audit_result.get("risk_score", 0)

                # Verdict display
                if verdict == "APPROVED":
                    st.markdown(f"""
                    <div class="verdict-approved">
                        <div style="font-size: 2rem;">✅</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #166534;">APPROVED</div>
                        <div style="color: #166534;">Ready for reimbursement</div>
                        <div style="margin-top: 0.5rem;"><span class="badge badge-success">Risk Score: {risk_score}/100</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                elif verdict == "FLAGGED_FOR_REVIEW":
                    st.markdown(f"""
                    <div class="verdict-flagged">
                        <div style="font-size: 2rem;">⚠️</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #92400e;">FLAGGED FOR REVIEW</div>
                        <div style="color: #92400e;">Requires accountant verification</div>
                        <div style="margin-top: 0.5rem;"><span class="badge badge-warning">Risk Score: {risk_score}/100</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <div class="verdict-rejected">
                        <div style="font-size: 2rem;">❌</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #991b1b;">REJECTED</div>
                        <div style="color: #991b1b;">Compliance violations detected</div>
                        <div style="margin-top: 0.5rem;"><span class="badge badge-error">Risk Score: {risk_score}/100</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("")

                # Audit findings
                st.markdown("**Compliance Checks:**")

                for finding in audit_result.get("findings", []):
                    sev = finding.get("severity", "INFO")
                    rule = finding.get("rule", "Unknown")
                    msg = finding.get("message", "")

                    if sev == "PASSED":
                        st.markdown(f"""
                        <div class="finding-item finding-pass">
                            <span class="badge badge-success">PASS</span>
                            <strong style="margin-left: 0.5rem;">{rule}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                    elif sev == "CRITICAL":
                        st.markdown(f"""
                        <div class="finding-item finding-critical">
                            <span class="badge badge-error">CRITICAL</span>
                            <strong style="margin-left: 0.5rem;">{rule}</strong>
                            <div style="margin-top: 0.25rem; font-size: 0.9rem; color: #991b1b;">{msg}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    elif sev == "WARNING":
                        st.markdown(f"""
                        <div class="finding-item finding-warn">
                            <span class="badge badge-warning">WARNING</span>
                            <strong style="margin-left: 0.5rem;">{rule}</strong>
                            <div style="margin-top: 0.25rem; font-size: 0.9rem; color: #92400e;">{msg}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    elif sev == "INFO":
                        st.markdown(f"""
                        <div style="padding: 0.75rem 1rem; background: #f0f9ff; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #3b82f6;">
                            <span class="badge badge-info">INFO</span>
                            <strong style="margin-left: 0.5rem;">{rule}</strong>
                            <div style="margin-top: 0.25rem; font-size: 0.9rem; color: #1e40af;">{msg}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Cryptographic seal
                sig = meta.get("verification_signature", "")
                if sig:
                    st.markdown("**🔐 Cryptographic Audit Seal (SHA-256):**")
                    st.markdown(f'<div class="seal-box">{sig}</div>', unsafe_allow_html=True)

                st.markdown("---")

                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.button("✅ Approve & Submit", type="primary", use_container_width=True)
                with col_btn2:
                    # Build export report
                    export_report = {
                        "report_generated": datetime.now().isoformat(),
                        "verdict": verdict,
                        "risk_score": risk_score,
                        "calculations": {
                            "per_diem_czk": meta.get("total_stravne_czk", 0),
                            "meal_deductions_czk": meta.get("total_kraceni_czk", 0),
                            "pocket_money_czk": meta.get("total_kapesne_czk", 0),
                        },
                        "compliance_findings": audit_result.get("findings", []),
                        "cryptographic_seal": meta.get("verification_signature", ""),
                        "documents_processed": len(extractions),
                        "document_extractions": extractions,
                        "trip_data": merged_data,
                        "full_calculation": calc_result
                    }
                    report_json = json.dumps(export_report, indent=2, default=str)
                    st.download_button(
                        "📤 Export Report",
                        data=report_json,
                        file_name=f"perdiemo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

        else:
            # Empty state
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; color: #64748b;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
                <div style="font-size: 1.25rem; font-weight: 500; margin-bottom: 1rem;">
                    Upload receipts to begin processing
                </div>
                <div style="max-width: 400px; margin: 0 auto; text-align: left;">
                    <div style="margin-bottom: 0.5rem;">The system will:</div>
                    <div>✓ Extract data from each document</div>
                    <div>✓ Calculate statutory per diems</div>
                    <div>✓ Run compliance checks</div>
                    <div>✓ Generate auditable report</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_text:
    st.markdown('<div class="section-header">💬 Describe Your Business Trip</div>', unsafe_allow_html=True)

    col_text_input, col_text_result = st.columns([1, 1], gap="large")

    with col_text_input:
        sample_text = (
            "Departed Prague on June 10, 2025 at 07:00 AM by company car to Vienna for client meetings. "
            "Crossed the border at Mikulov at 09:30 AM, arrived in Vienna at 11:00 AM. "
            "Overnight at Grand Hotel Wien with complimentary breakfast included in room rate. "
            "On June 11 departed Vienna at 16:00, crossed border back into Czechia at 17:30, arrived in Prague at 20:00."
        )

        trip_description = st.text_area(
            "Enter trip details in natural language:",
            value=sample_text,
            height=200,
            help="Describe your trip including dates, locations, transport, hotels, and meals"
        )

        text_year = st.selectbox("Tax Year", [2025, 2026], index=0, key="text_year")

        text_process_btn = st.button(
            "🚀 Process Trip Description",
            type="primary",
            use_container_width=True,
            key="text_process"
        )

    with col_text_result:
        if text_process_btn and trip_description:
            with st.spinner("🤖 AI parsing trip description..."):
                text_extraction = agent.extract_from_text(trip_description)

            st.markdown("### 📋 Extracted Itinerary")

            # Show extracted data
            if text_extraction.get("ucel_cesty"):
                st.markdown(f"**Purpose:** {text_extraction['ucel_cesty']}")

            if text_extraction.get("hotel_info", {}).get("hotel_name"):
                h = text_extraction["hotel_info"]
                breakfast = "✅ Included" if h.get("breakfast_included") else "❌ Not included"
                st.markdown(f"**Hotel:** {h['hotel_name']} — Breakfast: {breakfast}")

            if text_extraction.get("itinerary"):
                st.markdown("**Itinerary:**")
                for leg in text_extraction["itinerary"]:
                    st.markdown(f"• `{leg.get('typ')}` {leg.get('datum', '')} — {leg.get('misto', '')} ({leg.get('country_code', '')})")

            if text_extraction.get("bezplatna_strava"):
                st.markdown("**Free meals declared:**")
                for date, meals in text_extraction["bezplatna_strava"].items():
                    st.markdown(f"• {date}: {', '.join(meals)}")

            st.markdown("---")

            # Calculate per diems
            with st.spinner("Computing per diems..."):
                text_trip = [{
                    "id_cesty": "TEXT-DEMO-001",
                    "ucel_cesty": text_extraction.get("ucel_cesty", "Business"),
                    "vlastnictvi_vozidla": text_extraction.get("typ_vozidla", "SLUZEBNI"),
                    "zamestnanec_jednatel": text_extraction.get("zamestnanec_jednatel", "Employee"),
                    "spolecnost": "KB Client",
                    "bezplatna_strava": text_extraction.get("bezplatna_strava", {}),
                    "itinerar": text_extraction.get("itinerary", [])
                }]
                text_calc = client.calculate(text_trip, year=text_year)

            text_meta = text_calc.get("metadata", {})

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Per Diem", f"{text_meta.get('total_stravne_czk', 0):,.0f} CZK")
            with col_m2:
                st.metric("Deductions", f"-{text_meta.get('total_kraceni_czk', 0):,.0f} CZK")

            # Audit
            text_merged = {
                "ucel_cesty": text_extraction.get("ucel_cesty"),
                "hotel_info": text_extraction.get("hotel_info", {}),
                "bezplatna_strava": text_extraction.get("bezplatna_strava", {}),
                "itinerary": text_extraction.get("itinerary", [])
            }
            text_audit = auditor.audit_trip(text_merged, text_calc)

            verdict = text_audit.get("verdict")
            risk = text_audit.get("risk_score", 0)

            st.markdown("### 🛡️ Compliance Audit")

            if verdict == "APPROVED":
                st.success(f"✅ **APPROVED** — Risk: {risk}/100")
            elif verdict == "FLAGGED_FOR_REVIEW":
                st.warning(f"⚠️ **FLAGGED** — Risk: {risk}/100")
            else:
                st.error(f"❌ **REJECTED** — Risk: {risk}/100")

            st.markdown("**Compliance Checks:**")

            for finding in text_audit.get("findings", []):
                sev = finding.get("severity")
                rule = finding.get("rule", "")
                msg = finding.get("message", "")

                if sev == "CRITICAL":
                    st.markdown(f"""
                    <div class="finding-item finding-critical">
                        <span class="badge badge-error">CRITICAL</span>
                        <strong style="margin-left: 0.5rem;">{rule}</strong>
                        <div style="margin-top: 0.25rem; font-size: 0.9rem;">{msg}</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif sev == "WARNING":
                    st.markdown(f"""
                    <div class="finding-item finding-warn">
                        <span class="badge badge-warning">WARNING</span>
                        <strong style="margin-left: 0.5rem;">{rule}</strong>
                        <div style="margin-top: 0.25rem; font-size: 0.9rem;">{msg}</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif sev == "PASSED":
                    st.markdown(f"""
                    <div class="finding-item finding-pass">
                        <span class="badge badge-success">PASS</span>
                        <strong style="margin-left: 0.5rem;">{rule}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                elif sev == "INFO":
                    st.markdown(f"""
                    <div style="padding: 0.5rem; background: #f0f9ff; border-radius: 6px; margin-bottom: 0.5rem; border-left: 4px solid #3b82f6;">
                        <span class="badge badge-info">INFO</span>
                        <strong style="margin-left: 0.5rem;">{rule}</strong>
                        <div style="margin-top: 0.25rem; font-size: 0.9rem;">{msg}</div>
                    </div>
                    """, unsafe_allow_html=True)

            sig = text_meta.get("verification_signature", "")
            if sig:
                st.markdown(f"**🔐 Seal:** `{sig[:40]}...`")

        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                <div>Describe your trip in natural language</div>
                <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                    AI will extract dates, locations, hotels, and meals automatically
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_about:
    st.markdown("""
    ## About PerDiemo

    **PerDiemo** automates corporate travel expense processing and compliance auditing for back-office teams.

    ### The Problem
    - Travel expense reporting is error-prone and time-consuming
    - Czech Labour Code (§§ 151-189) has complex per diem rules
    - Manual verification of receipts against declarations
    - Risk of meal double-dipping and expense fraud

    ### Our Solution
    1. **AI Document Extraction** — AWS Bedrock Claude extracts data from receipts
    2. **Statutory Calculation** — PerDiemo API computes per diems per Czech law
    3. **Compliance Audit** — Rule engine detects anomalies and fraud
    4. **Cryptographic Seal** — SHA-256 signature for audit defense

    ### Technology Stack
    - **AI/ML:** AWS Bedrock (Claude Sonnet 4.5)
    - **Calculation Engine:** PerDiemo Statutory API
    - **Frontend:** Streamlit
    - **Compliance:** KB Back-Office Rules Engine

    ---

    **The FinTechers Hackathon 2026** — Track 06: Finance Operations & Back-Office AI

    Built by Team PerDiemo
    """)
