# POAM-Automation

Step-by-Step Overview
Step 1: Monthly POAM Sheet Prep
You receive a new .xlsx file of POAM data each month.

You run your Excel-to-CSV converter script to generate a Jira-compatible CSV.

The output file is named like:
poam/2024-07.csv

Step 2: Upload to S3
You upload the new CSV file to an S3 bucket, for example:


s3://your-bucket-name/poam/2024-07.csv
Step 3: Jira Auto-Ticket Creation (if needed)
Jira Automation Rule watches for new uploads or CSV imports.

When the new CSV is imported into Jira, tickets are created for new POAM items.

These tickets contain the POAM ID, Summary, Description, etc.

Step 4: Lambda Function for Cleanup
On a schedule (e.g., every month), your AWS Lambda function runs.

The function:

Downloads two files from S3:
previous.csv (e.g., 2024-06.csv) and current.csv (e.g., 2024-07.csv)

Extracts all POAM IDs from each.

Compares them to find POAMs that existed last month but are now gone.

For each missing POAM:

Queries Jira to find any open ticket containing that POAM ID.

Transitions the ticket to "Done" or "Closed" using the Jira API.

Step 5: Tickets Closed Automatically
Any Jira ticket for a resolved POAM is automatically closed.

Result: Your Jira dashboard stays clean, showing only active/remediating POAMs.

Summary Flow Diagram

POAM Excel (.xlsx) → CSV → S3 Bucket
                                ↓
         Jira auto-creates tickets from CSV import
                                ↓
    Scheduled Lambda → Downloads old & new CSV from S3
                                ↓
   Compares POAM IDs → Finds resolved ones → Closes Jira tickets


