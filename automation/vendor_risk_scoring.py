import pandas as pd

vendors = pd.read_csv("vendor-inventory.csv")

score_map = {
    "PHI": 5,
    "PCI/PII": 5,
    "PII": 3,
    "Internal Data": 2,
    "Customer Data": 3
}

access_map = {
    "Privileged": 5,
    "Limited": 3,
    "Standard": 2
}

criticality_map = {
    "High": 5,
    "Medium": 3,
    "Low": 1
}

vendors["Risk_Score"] = (
    vendors["Data_Processed"].map(score_map) +
    vendors["Access_Level"].map(access_map) +
    vendors["Criticality"].map(criticality_map)
)

def assign_tier(score):
    if score >= 13:
        return "Critical"
    elif score >= 10:
        return "High"
    elif score >= 7:
        return "Medium"
    return "Low"

vendors["Risk_Tier"] = vendors["Risk_Score"].apply(assign_tier)

vendors.to_csv("vendor-risk-results.csv", index=False)

print(vendors)