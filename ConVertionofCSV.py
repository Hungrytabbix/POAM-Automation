import pandas as pd
import os
import argparse as arg

def main():
    parser = arg.ArgumentParser(description='Translate Overdue POAMs Excel file to Jira import CSV.')
    parser.add_argument("--file", type=str, required=True, help="Path to the Excel file (.xlsx)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return

    try:
        convert_to_csv(args.file)
    except Exception as e:
        print(f"❌ Error: {e}")

def convert_to_csv(filename):
    # Column names taken from Excel screenshot
    column_names = [
        "POAM ID", "Controls", "Weakness Name", "Weakness Description",
        "Weakness Detector Source", "Weakness Source Identifier", "Asset Identifier",
        "Point of Contact", "Request Required", "Overall Remediation",
        "Original/Detected Date", "Scheduled Completion", "Planned Milestones",
        "Milestone Changes", "Status", "Vendor Depend", "Last Verified Check Date",
        "Vendor Depend Details", "Original Rating", "Adjusted Rating", "Risk Adjust",
        "False Pos", "Operat Req", "Operation Rationale", "Supporting Document",
        "Comments", "Auto-App", "Binding Operat Directive 23-02 Applic", 
        "Binding Operat Directive 23-02 Date", "CVE", "Service Now"
    ]

    df = pd.read_excel(filename, header=None, names=column_names)

    # Confirm expected columns
    for col in ["POAM ID", "Weakness Name", "Weakness Description", "Weakness Detector Source",
                "Original Rating", "Overall Remediation", "Asset Identifier",
                "Point of Contact", "Scheduled Completion", "CVE"]:
        if col not in df.columns:
            raise Exception(f"Missing required column: '{col}'")

    # Compose Jira fields
    df['Summary'] = "POAM ID: " + df['POAM ID'].astype(str)
    df['Description'] = (
        df['Weakness Name'].astype(str) + ' ' +
        df['Weakness Description'].astype(str) + ' ' +
        df['Weakness Detector Source'].astype(str) + ' ' +
        df['Original Rating'].astype(str) + ' ' +
        df['Overall Remediation'].astype(str) + ' ' +
        df['Asset Identifier'].astype(str)
    )
    df['Group'] = df['Point of Contact']
    df['Requested Completion Date'] = pd.to_datetime(df['Scheduled Completion'], errors='coerce').dt.date
    df['CVE'] = df['CVE'].astype(str)

    # Final output
    export = df[['Summary', 'Description', 'Group', 'Requested Completion Date', 'POAM ID', 'CVE']]
    output_filename = filename.replace('.xlsx', ' Jira Import File.csv')
    export.to_csv(output_filename, index=False)
    print(f"✅ Jira import file created: {output_filename}")

if __name__ == "__main__":
    main()
