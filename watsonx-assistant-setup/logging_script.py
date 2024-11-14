import requests
import csv
import os
import sys
import datetime
import argparse

# Ensure necessary environment variables are set
required_env_vars = ['ASSISTANT_ENVIRONMENT_ID', 'ASSISTANT_URL', 'ASSISTANT_API_KEY']
for var in required_env_vars:
    if var not in os.environ:
        sys.exit(f"{var} is not set in the environment. Please set it before running the script.")

# Parse optional arguments
parser = argparse.ArgumentParser(description="Retrieve Watson Assistant logs and save them to a CSV file.")
parser.add_argument('--filter', type=str, default='response_timestamp>2024-11-01T04:00:00.000Z',
                    help="Filter for retrieving logs (default: 'response_timestamp>2024-11-01T04:00:00.000Z')")
args = parser.parse_args()

# Retrieve environment variables
environmentID = os.environ['ASSISTANT_ENVIRONMENT_ID']
url = f"{os.environ['ASSISTANT_URL']}/v2/assistants/{environmentID}/logs"
apikey = os.environ['ASSISTANT_API_KEY']
version = "2024-08-25"

# Set up CSV filename
now = datetime.datetime.now()
csv_filename = f"{now.strftime('%Y-%m-%dT%H_%M')}_feedback.csv"

def get_watson_assistant_logs(url, apikey, params):
    """Fetch logs from the Watson Assistant API."""
    response = requests.get(url, auth=('apikey', apikey), params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve logs. Status code: {response.status_code}")
        return None

def format_feedback(feedback_payload):
    if "rag_response" not in feedback_payload:
        feedback_payload['rag_response'] = 'Not Provided'
    
    rag_response = feedback_payload["rag_response"]
    if type(rag_response) == str and rag_response != '':
        rag_response = rag_response.lstrip('\n')
        if "<br><br>References: <ol type='1'>  " in rag_response:
            references = rag_response.split("<br><br>References: <ol type='1'>  ")
            formatted_references = references[1].replace("</li>", ";").replace("<li>", "").replace("</ol>", "")
            feedback_payload["rag_response"] = references[0] +"\n"+ formatted_references
        return feedback_payload
    else:
        return feedback_payload
    
def extract_feedback_payloads(logs):
    """Extract feedback payloads with 'rag_response' field from logs."""
    feedback_payloads = []
    seen_payloads = set()  # Track unique entries to avoid duplicates

    for log in logs:
        skills = log.get('response', {}).get('context', {}).get('skills', {}).get('actions skill', {}).get('skill_variables', {})
        feedback_payload = skills.get('feedback_payload', {})
        feedback_payload = format_feedback(feedback_payload)

        # Ensure feedback_payload has 'rag_response' and is unique
#        if feedback_payload and "rag_response" in feedback_payload:
        if feedback_payload:
            unique_key = tuple(feedback_payload.get(key, '') for key in ["comments", "query", "rating", "llm_response", "rag_response"])
            if unique_key not in seen_payloads:
                feedback_payload["date_time"] = feedback_payload.get("date_time", "None")
                feedback_payloads.append(feedback_payload)
                seen_payloads.add(unique_key)
            # else:
            #     print(f"Skipping duplicate feedback payload: {feedback_payload.get('query', 'unknown query')}")
    return feedback_payloads

# Retrieve all logs with pagination handling
def retrieve_all_logs():
    logs = []
    cursor = None
    while True:
        params = {
            'version': version,
            'sort': '-request_timestamp',
            'filter': args.filter
        }
        if cursor:
            params['cursor'] = cursor

        response = get_watson_assistant_logs(url, apikey, params)
        if not response:
            break
        logs.extend(response["logs"])
        cursor = response.get("pagination", {}).get("next_cursor")

        # Exit if there's no further pagination
        if not cursor:
            break

    return logs

# Main execution
logs = retrieve_all_logs()
if logs:
    feedback_payloads = extract_feedback_payloads(logs)

    # Define CSV columns and write data
    column_names = ["date_time", "query", "llm_response", "rag_response", "rating", "comments"]
    with open(csv_filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(feedback_payloads)

    print(f"Data written to {csv_filename}")
else:
    print("No logs retrieved.")
