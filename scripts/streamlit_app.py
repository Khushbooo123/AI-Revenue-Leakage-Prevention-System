
import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Revenue Leakage System", layout="wide")

st.title("AI-Driven Revenue Leakage Prevention System")
st.markdown("Upload CRM, Billing, and Onboarding datasets to detect revenue leakage risks.")

# File Uploaders
crm_file = st.file_uploader("Upload CRM File (Excel)", type=["xlsx"])
billing_file = st.file_uploader("Upload Billing File (Excel)", type=["xlsx"])
onboarding_file = st.file_uploader("Upload Onboarding File (Excel)", type=["xlsx"])

if crm_file and billing_file and onboarding_file:

    crm = pd.read_excel(crm_file)
    billing = pd.read_excel(billing_file)
    onboarding = pd.read_excel(onboarding_file)

    merged = crm.merge(billing, on="Customer_ID", how="left")
    merged = merged.merge(onboarding, on="Customer_ID", how="left")

    risk_flags = []
    severity_scores = []

    for index, row in merged.iterrows():
        issues = []
        severity = 0
        
        # Missing Invoice
        if pd.isna(row["Invoice_Amount"]):
            issues.append("Missing Invoice")
            severity += 3
        
        # Billing Mismatch
        elif row["Deal_Value"] != row["Invoice_Amount"]:
            issues.append("Billing Mismatch")
            severity += 2
        
        # Onboarding Delay
        delay = (row["Onboarding_Completion_Date"] - row["Deal_Close_Date"]).days
        if delay > 10:
            issues.append("Onboarding Delay Risk")
            severity += 1
        
        risk_flags.append(", ".join(issues) if issues else "No Risk")
        severity_scores.append(severity)

    merged["Risk_Flags"] = risk_flags
    merged["Severity_Score"] = severity_scores

    risk_cases = merged[merged["Severity_Score"] > 0]

    st.subheader("Executive Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Deals", len(crm))
    col2.metric("Total Risk Cases", len(risk_cases))

    st.subheader("Detected Risk Cases")
    st.dataframe(risk_cases)

    st.download_button(
        label="Download Risk Report as CSV",
        data=risk_cases.to_csv(index=False),
        file_name="revenue_leakage_report.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload all three datasets to proceed.")
