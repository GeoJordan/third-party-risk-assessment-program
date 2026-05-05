import seaborn as sns
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

VENDOR_FILE = DATA_DIR / "vendor-inventory.csv"
FINDINGS_FILE = DATA_DIR / "vendor-findings.csv"
RESULTS_FILE = OUTPUT_DIR / "vendor-risk-results.csv"

st.set_page_config(
    page_title="TPRM Risk Assessment Platform",
    layout="wide"
)

st.title("Third-Party Risk Management Assessment Platform")

st.sidebar.markdown("""
### Overview
This application simulates an enterprise-style Third-Party Risk Management workflow.

### Framework Alignment
- NIST SP 800-161
- ISO/IEC 27036
- Shared Assessments SIG Concepts

### Risk Tier Legend
- **Critical:** 20–25  
- **High:** 15–19  
- **Medium:** 10–14  
- **Low:** 5–9  

### Author
George Jordan
""")

data_score = {
    "Public": 1,
    "Internal Data": 2,
    "PII": 3,
    "Customer Data": 3,
    "PHI": 5,
    "PCI/PII": 5
}

access_score = {
    "None": 1,
    "Standard": 2,
    "Limited": 3,
    "Privileged": 5
}

criticality_score = {
    "Low": 1,
    "Medium": 3,
    "High": 5
}

regulatory_score = {
    "None": 0,
    "Low": 1,
    "Moderate": 3,
    "High": 5
}

hosting_score = {
    "No Hosting": 1,
    "Partial Hosting": 3,
    "Full Hosting": 5
}

def assign_tier(score):
    if score >= 20:
        return "Critical"
    elif score >= 15:
        return "High"
    elif score >= 10:
        return "Medium"
    return "Low"

def calculate_score(data, access, criticality, regulatory, hosting):
    return (
        data_score[data]
        + access_score[access]
        + criticality_score[criticality]
        + regulatory_score[regulatory]
        + hosting_score[hosting]
    )

def load_vendors():
    if VENDOR_FILE.exists():
        return pd.read_csv(VENDOR_FILE)

    return pd.DataFrame(columns=[
        "Vendor",
        "Service",
        "Data_Processed",
        "Access_Level",
        "Criticality",
        "Regulatory_Exposure",
        "Hosting_Responsibility",
        "Inherent_Risk_Score",
        "Risk_Tier",
        "Assessment_Status"
    ])

def save_vendors(df):
    df.to_csv(VENDOR_FILE, index=False)
    df.to_csv(RESULTS_FILE, index=False)

def load_findings():
    if FINDINGS_FILE.exists():
        return pd.read_csv(FINDINGS_FILE)

    df = pd.DataFrame({
        "Finding_ID": ["F-001", "F-002", "F-003"],
        "Vendor": ["MedCloud Hosting", "RecruitTrack", "SlackClone"],
        "Domain": ["BCP/DR", "Access Management", "Vulnerability Management"],
        "Severity": ["High", "High", "Medium"],
        "Status": ["Open", "Open", "Risk Accepted"],
        "Owner": ["CISO", "IT Director", "Security Manager"],
        "Due_Date": ["2026-09-30", "2026-07-01", "2026-06-15"]
    })

    df.to_csv(FINDINGS_FILE, index=False)
    return df

vendors = load_vendors()
findings = load_findings()

vendors = vendors.sort_values(
    by="Inherent_Risk_Score",
    ascending=False
)

def highlight_risk_tier(value):
    if value == "Critical":
        return "background-color: #ff4d4d; color: white; font-weight: bold"
    elif value == "High":
        return "background-color: #ffcc00; color: black; font-weight: bold"
    elif value == "Medium":
        return "background-color: #fff2cc; color: black"
    elif value == "Low":
        return "background-color: #d9ead3; color: black"
    return ""

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Vendor Intake",
    "Vendor Inventory",
    "Findings Tracker",
    "Dashboard",
    "Risk Heatmap"
])

with tab1:
    st.header("Vendor Intake & Risk Tiering")

    with st.form("vendor_intake_form"):
        vendor = st.text_input("Vendor Name")
        service = st.text_input("Service Provided")

        data = st.selectbox("Data Processed", list(data_score.keys()))
        access = st.selectbox("Access Level", list(access_score.keys()))
        criticality = st.selectbox("Business Criticality", list(criticality_score.keys()))
        regulatory = st.selectbox("Regulatory Exposure", list(regulatory_score.keys()))
        hosting = st.selectbox("Hosting Responsibility", list(hosting_score.keys()))

        submitted = st.form_submit_button("Calculate and Save Vendor")

        if submitted:
            if not vendor.strip() or not service.strip():
                st.error("Vendor Name and Service Provided are required.")
                st.stop()

            if vendor.lower().strip() in vendors["Vendor"].str.lower().str.strip().values:
                st.warning("Vendor already exists in inventory.")
                st.stop()
            
            score = calculate_score(data, access, criticality, regulatory, hosting)
            tier = assign_tier(score)

            new_vendor = pd.DataFrame([{
                "Vendor": vendor,
                "Service": service,
                "Data_Processed": data,
                "Access_Level": access,
                "Criticality": criticality,
                "Regulatory_Exposure": regulatory,
                "Hosting_Responsibility": hosting,
                "Inherent_Risk_Score": score,
                "Risk_Tier": tier,
                "Assessment_Status": "Pending Review"
                }])

            vendors = pd.concat([vendors, new_vendor], ignore_index=True)
            save_vendors(vendors)
            
            st.success(f"{vendor} saved. Inherent Risk Score: {score}. Risk Tier: {tier}")
        
    
with tab2:
    st.header("Vendor Inventory")

    st.dataframe(
        vendors.style.map(
            highlight_risk_tier,
            subset=["Risk_Tier"]
        ),
        use_container_width=True
    )

    if not vendors.empty:
        csv = vendors.to_csv(index=False)

        st.download_button(
            label="Download Vendor Risk Results",
            data=csv,
            file_name="vendor-risk-results.csv",
            mime="text/csv"
        )

        if st.button("Clear Vendor Inventory"):
            vendors = vendors.iloc[0:0]
            save_vendors(vendors)
            st.success("Vendor inventory cleared.")
            st.rerun()

with tab3:
    st.header("Findings Tracker")
    st.dataframe(findings, use_container_width=True)

with tab4:
    st.header("Executive Dashboard")

    if vendors.empty:
        st.info("Add vendors in the Vendor Intake tab to populate dashboard metrics.")
    else:
        total_vendors = len(vendors)
        high_risk = vendors[vendors["Risk_Tier"].isin(["High", "Critical"])].shape[0]
        open_findings = findings[findings["Status"] == "Open"].shape[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Vendors", total_vendors)
        col2.metric("High/Critical Vendors", high_risk)
        col3.metric("Open Findings", open_findings)

        st.subheader("Vendors by Risk Tier")
        tier_counts = vendors["Risk_Tier"].value_counts()

        fig, ax = plt.subplots()
        tier_counts.plot(kind="bar", ax=ax)
        ax.set_xlabel("Risk Tier")
        ax.set_ylabel("Vendor Count")
        ax.set_title("Vendor Risk Tier Distribution")
        st.pyplot(fig)

        st.subheader("Findings by Severity")
        severity_counts = findings["Severity"].value_counts()

        fig2, ax2 = plt.subplots()
        severity_counts.plot(kind="bar", ax=ax2)
        ax2.set_xlabel("Severity")
        ax2.set_ylabel("Finding Count")
        ax2.set_title("Findings Severity Distribution")
        st.pyplot(fig2)

with tab5:
    st.header("Vendor Risk Heatmap")

    if vendors.empty:
        st.info("Add vendors in the Vendor Intake tab to populate the heatmap.")
    else:
        heatmap_data = pd.crosstab(
            vendors["Risk_Tier"],
            vendors["Assessment_Status"]
        )

        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="d",
            cmap="YlOrRd",
            ax=ax3
        )

        ax3.set_title("Risk Tier vs Assessment Status")
        ax3.set_xlabel("Assessment Status")
        ax3.set_ylabel("Risk Tier")

        st.pyplot(fig3)
        
st.caption("For educational and portfolio demonstration purposes only.")
        