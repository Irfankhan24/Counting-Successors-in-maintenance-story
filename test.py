import requests
from requests.auth import HTTPBasicAuth
import os 
from dotenv import load_dotenv

load_dotenv()
ORG_NAME = "rapyuta-robotics"
PROJECT_NAME = "Oks"
PAT =os.getenv('PAT')

WORK_ITEM_URL_TEMPLATE = f"https://dev.azure.com/{ORG_NAME}/{PROJECT_NAME}/_apis/wit/workitems/{{}}?$expand=relations&api-version=7.0"
UPDATE_WORK_ITEM_URL_TEMPLATE = f"https://dev.azure.com/{ORG_NAME}/{PROJECT_NAME}/_apis/wit/workitems/{{}}?api-version=7.0"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH = HTTPBasicAuth("", PAT)

work_item_id = input("Enter the Work Item ID you want to check: ").strip()

work_item_url = WORK_ITEM_URL_TEMPLATE.format(work_item_id)
work_item_resp = requests.get(work_item_url, headers=HEADERS, auth=AUTH)
if work_item_resp.status_code == 200:
    work_item_data = work_item_resp.json()
    successor_count = 0
    
    if "relations" in work_item_data:
        for relation in work_item_data["relations"]:
            if relation.get("rel") == "System.LinkTypes.Dependency-Forward":
                successor_count += 1

    update_url = UPDATE_WORK_ITEM_URL_TEMPLATE.format(work_item_id)
    update_data = [
        {
            "op": "add",
            "path": "/fields/Custom.IssueInstancesCount", 
            "value": successor_count
        }
    ]
    update_headers = {
        "Content-Type": "application/json-patch+json",
        "Accept": "application/json"
    }
    update_resp = requests.patch(update_url, json=update_data, headers=update_headers, auth=AUTH)
    if update_resp.status_code in [200, 201]:
        print(f"Issue Instances Count = {successor_count}")
    else:
        print(f"Failed to update Work Item {work_item_id}. Status: {update_resp.status_code}, Error: {update_resp.text}")
else:
    print(f"Error fetching work item {work_item_id}: {work_item_resp.status_code}, {work_item_resp.text}")