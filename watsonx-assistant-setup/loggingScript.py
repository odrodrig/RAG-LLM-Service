import requests
import csv
import os
import sys
import datetime

# These 3 variables must be set in the environment for the script to work
if 'ASSISTANT_ENVIRONMENT_ID' not in os.environ:
    sys.exit("ASSISTANT_ENVIRONMENT_ID is not set in the environment. Please set it before running the script. Refer to the readme for more information.")
if 'ASSISTANT_URL' not in os.environ:
    sys.exit("ASSISTANT_URL is not set in the environment. Please set it before running the script. Refer to the readme for more information.")
if 'ASSISTANT_API_KEY' not in os.environ:
    sys.exit("ASSISTANT_API_KEY is not set in the environment. Please set it before running the script. Refer to the readme for more information.")

# Variables that will be pulled from the environment
environmentID = os.environ['ASSISTANT_ENVIRONMENT_ID']
url = os.environ['ASSISTANT_URL']+"/v2/assistants/"+environmentID+"/logs"
apikey = os.environ['ASSISTANT_API_KEY']
version = "2024-08-25"

now = datetime.datetime.now()

currentTime = str(now.year) + "-" + str(now.month) +"-"+ str(now.day) + "T" + str(now.hour) + "_" + str(now.minute)

# File where the feedback will be saved locally
csvFilename = currentTime + "_" + "feedback.csv"

def get_watson_assistant_logs(url, apikey, params):
    """
    Makes a GET request to the Watson Assistant API to retrieve logs.

    Args:
        url (str): The URL of the Watson Assistant API.
        apikey (str): The API key for authentication.
        version (str): The version of the API.

    Returns:
        dict: The response from the API as a dictionary.
    """
    # params = {
    #     'version': version,
    #     'sort': '-request_timestamp'
    # }

    response = requests.get(url, auth=('apikey', apikey), params=params)

    if response.status_code == 200:

        return response.json()
    else:
        print(f"Failed to retrieve logs. Status code: {response.status_code}")
        return None

def formatReferences(feedback_payload):
    if "llm_response" not in feedback_payload:
        feedback_payload['llm_response'] = 'Not Provided'

    llm_response = feedback_payload["llm_response"]
    if type(llm_response) == str and llm_response != '':
        llm_response = llm_response.lstrip('\n')
        if "<br><br>References: <ol type='1'>  " in llm_response:
            references = llm_response.split("<br><br>References: <ol type='1'>  ")
            formattedReferences = references[1].replace("</li>", ";").replace("<li>", "").replace("</ol>", "")
            feedback_payload["llm_response"] = references[0] +"\n"+ formattedReferences
        return feedback_payload
    else:
        return feedback_payload

def extract_feedback_payload(logs):
    """
    Extracts the feedback payload from the logs.

    Args:
        logs (dict): The logs retrieved from the Watson Assistant API.

    Returns:
        list: A list of feedback payloads.
    """
    feedback_payloads = []
    previousPayload = {}    

    # Loop through the logs to see if the feedback payload variable exists, if it does, store it in feedback_payloads
    # Will also filter out empty feedback_payloads and duplicates
    for log in logs:
        if 'response' in log and 'context' in log['response'] and 'skills' in log['response']['context']:
            skills = log['response']['context']['skills']
            if 'actions skill' in skills and 'skill_variables' in skills['actions skill']:
                skill_variables = skills['actions skill']['skill_variables']
                if 'feedback_payload' in skill_variables:
                    if skill_variables['feedback_payload'] != {}:
                        feedback_payload = skill_variables['feedback_payload']
                        feedback_payload = formatReferences(feedback_payload)
                        if feedback_payload != previousPayload:
                            if ("date_time" not in feedback_payload) or (type(feedback_payload["date_time"]) != str):
                                feedback_payload["date_time"] = "None"
                            feedback_payloads.append(feedback_payload)
                        
                        if ('date_time' in feedback_payload) and (feedback_payload['date_time'] == "None"):
                            previousPayload = {
                                "comments": feedback_payload["comments"],
                                "query": feedback_payload["query"],
                                "rating": feedback_payload["rating"],
                                "llm_response": feedback_payload["llm_response"],      
                            }
                        else:
                            previousPayload = feedback_payload
                    else: 
                        print("log removed")
                        logs.remove(log)

    return feedback_payloads

# Make the GET request and save the response as a dictionary
response = get_watson_assistant_logs(url, apikey, {
        'version': version,
        'sort': '-request_timestamp'
    })

logs = response["logs"]
if "next_cursor" in response["pagination"]:
    lastCursor = ""
    while response["pagination"]["next_cursor"] != lastCursor:
        response = get_watson_assistant_logs(url, apikey, {
            'version': version,
            'sort': '-request_timestamp',
            'cursor': response["pagination"]["next_cursor"]
        })
        for log in response["logs"]:
            logs.append(log)
        lastCursor = response["pagination"]["next_cursor"]

# If logs are successfully retrieved, then we create a CSV file and pass in the list of dictionaries containing the feedback_payloads
if logs is not None:
    print("Logs retrieved successfully:")
    feedback_payloads = extract_feedback_payload(logs)

    columnNames = [
        "date_time",
        "query",
        "llm_response",
        "rating",
        "comments"
    ]
    # Write the data to the CSV file
    with open(csvFilename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columnNames)
        writer.writeheader()
        writer.writerows(feedback_payloads)

    print(f"Data written to {csvFilename}")
