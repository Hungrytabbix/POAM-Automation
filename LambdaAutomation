import pandas as pd
import boto3
import requests
import os
import tempfile

# Setup clients and config
s3 = boto3.client('s3')
JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]
JIRA_USER = os.environ["JIRA_USER"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "POAM")
JIRA_HEADERS = {"Content-Type": "application/json"}

def download_s3_file(bucket, key):
    local_file = tempfile.NamedTemporaryFile(delete=False).name
    s3.download_file(bucket, key, local_file)
    return local_file

def read_poam_ids_from_csv(file_path):
    df = pd.read_csv(file_path)
    if "POAM ID" not in df.columns:
        raise Exception("Missing 'POAM ID' column in CSV")
    return set(df["POAM ID"].astype(str).unique())

def get_jira_issues_by_poam_id(poam_id):
    jql = f'project="{JIRA_PROJECT_KEY}" AND summary~"{poam_id}" AND statusCategory != Done'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    response = requests.get(
        url,
        headers=JIRA_HEADERS,
        auth=(JIRA_USER, JIRA_API_TOKEN),
        params={"jql": jql}
    )
    response.raise_for_status()
    return response.json().get("issues", [])

def transition_issue_to_closed(issue_key):
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/transitions"
    transitions = requests.get(url, headers=JIRA_HEADERS, auth=(JIRA_USER, JIRA_API_TOKEN)).json()["transitions"]
    done_transition = next((t for t in transitions if t["name"].lower() in ["done", "closed", "resolved"]), None)
    if not done_transition:
        print(f"No valid transition for {issue_key}")
        return
    requests.post(
        url,
        headers=JIRA_HEADERS,
        auth=(JIRA_USER, JIRA_API_TOKEN),
        json={"transition": {"id": done_transition["id"]}}
    )
    print(f"Closed Jira issue: {issue_key}")

def lambda_handler(event, context):
    # Expect event payload like:
    # {
    #   "bucket": "my-bucket",
    #   "previous_key": "poam/2024-06.csv",
    #   "current_key": "poam/2024-07.csv"
    # }

    bucket = event["bucket"]
    prev_key = event["previous_key"]
    curr_key = event["current_key"]

    prev_file = download_s3_file(bucket, prev_key)
    curr_file = download_s3_file(bucket, curr_key)

    prev_poams = read_poam_ids_from_csv(prev_file)
    curr_poams = read_poam_ids_from_csv(curr_file)
    resolved_poams = prev_poams - curr_poams

    for poam_id in resolved_poams:
        issues = get_jira_issues_by_poam_id(poam_id)
        for issue in issues:
            transition_issue_to_closed(issue["key"])

    os.remove(prev_file)
    os.remove(curr_file)

    return {
        "statusCode": 200,
        "resolved_poams": list(resolved_poams),
        "message": "Jira tickets closed for resolved POAMs"
    }
