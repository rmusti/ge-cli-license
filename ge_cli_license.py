# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import google.auth
import google.auth.transport.requests
import requests
import json
import os
import csv
import sys
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

def get_token(quota_project):
    try:
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform'],
            quota_project_id=quota_project
        )
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        return credentials.token
    except Exception as e:
        print(f"Failed to get token: {e}")
        return None

def fetch_all_user_licenses(project_id, location, user_store_id, quota_project):
    """Helper function to fetch all user licenses from the API."""
    base_url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/{location}/userStores/{user_store_id}/userLicenses"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    token = get_token(quota_project)
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    qp = quota_project or os.environ.get('PROJECT_ID')
    if qp:
        headers["X-Goog-User-Project"] = qp
        
    all_licenses = []
    next_page_token = None
    
    while True:
        url = base_url
        if next_page_token:
            url += f"?pageToken={next_page_token}"
            
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            licenses = data.get('userLicenses', [])
            all_licenses.extend(licenses)
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
            
    return all_licenses

def get_user_license(project_id, location, user_store_id, quota_project, user_principal):
    """Gets details for a specific user by filtering the list of all users."""
    print(f"Fetching user details for {user_principal}...")
    all_licenses = fetch_all_user_licenses(project_id, location, user_store_id, quota_project)
    
    for lic in all_licenses:
        if lic.get('userPrincipal') == user_principal:
            print(json.dumps(lic, indent=2))
            return
            
    print(f"Error: User {user_principal} not found.")
    sys.exit(1)

def list_user_licenses(project_id, location, user_store_id, quota_project, output_format=None, output_file=None):
    """Lists user licenses in a specific user store with pagination support."""
    print("Calling API...")
    all_licenses = fetch_all_user_licenses(project_id, location, user_store_id, quota_project)
            
    if not all_licenses:
        print("No user licenses found.")
        return

    if output_format == 'json':
        content = json.dumps(all_licenses, indent=2)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"Saved {len(all_licenses)} users to {output_file}")
        else:
            print(content)
        return

    if output_format == 'csv':
        keys = all_licenses[0].keys()
        if output_file:
            with open(output_file, 'w', newline='') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_licenses)
            print(f"Saved {len(all_licenses)} users to {output_file}")
        else:
            dict_writer = csv.DictWriter(sys.stdout, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_licenses)
        return
        
    header_fmt = "{:<40} | {:<20} | {:<30}"
    print(header_fmt.format("User Principal", "Assignment State", "Update Time"))
    print("-" * 95)
    
    for lic in all_licenses:
        user = lic.get('userPrincipal', 'N/A')
        state = lic.get('licenseAssignmentState', 'N/A')
        update_time = lic.get('updateTime', 'N/A')
        print(header_fmt.format(user, state, update_time))
    
    print(f"\nTotal users found: {len(all_licenses)}")

def batch_update_licenses(project_id, location, user_store_id, user_licenses_list, quota_project, delete_unassigned=False, update_mask=None):
    """Batch updates user licenses using inlineSource.userLicenses."""
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/{location}/userStores/{user_store_id}:batchUpdateUserLicenses"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    token = get_token(quota_project)
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    qp = quota_project or os.environ.get('PROJECT_ID')
    if qp:
        headers["X-Goog-User-Project"] = qp

    # Chunk size of 100
    chunk_size = 100
    total_users = len(user_licenses_list)
    print(f"Starting batch update for {total_users} users...")

    for i in range(0, total_users, chunk_size):
        chunk = user_licenses_list[i : i + chunk_size]
        
        # The V1 API expects:
        # {
        #   "inlineSource": { "userLicenses": [...] },
        #   "deleteUnassignedUserLicenses": bool,
        #   "updateMask": string
        # }
        batch_payload = {
            "inlineSource": {
                "userLicenses": chunk
            },
            "deleteUnassignedUserLicenses": delete_unassigned
        }
        
        if update_mask:
            batch_payload["inlineSource"]["updateMask"] = update_mask
        
        print(f"Updating batch {i//chunk_size + 1} (Users {i+1} to {min(i+chunk_size, total_users)})...")
        response = requests.post(url, headers=headers, json=batch_payload)
        
        if response.status_code == 200:
            print(f"Batch {i//chunk_size + 1} successful.")
        else:
            print(f"Error in batch {i//chunk_size + 1}: {response.status_code}")
            print(response.text)
    
    print("Batch update process completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Enterprise License CLI (Discovery Engine)")
    
    default_project = os.environ.get('PROJECT_ID')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List user licenses')
    parser_list.add_argument("--project", default=default_project, help="GCP Project ID")
    parser_list.add_argument("--location", default="global", help="Location (default: global)")
    parser_list.add_argument("--user-store", default="default_user_store", help="User Store ID (default: default_user_store)")
    parser_list.add_argument("--quota-project", help="GCP Project ID for quota/billing")
    parser_list.add_argument("--format", choices=['table', 'json', 'csv'], default='table', help="Output format")
    parser_list.add_argument("--output", help="Output file path")

    # Get command
    parser_get = subparsers.add_parser('get', help='Get details for a specific user')
    parser_get.add_argument("user_principal", help="Email of the user")
    parser_get.add_argument("--project", default=default_project, help="GCP Project ID")
    parser_get.add_argument("--location", default="global", help="Location (default: global)")
    parser_get.add_argument("--user-store", default="default_user_store", help="User Store ID (default: default_user_store)")
    parser_get.add_argument("--quota-project", help="GCP Project ID for quota/billing")
    
    # Update command (Single user)
    parser_update = subparsers.add_parser('update', help='Update or add a single user license')
    parser_update.add_argument("user_principal", help="Email of the user")
    parser_update.add_argument("--state", choices=['ASSIGNED', 'UNASSIGNED'], default='ASSIGNED', help="Assignment state")
    parser_update.add_argument("--config", help="License config path (optional if already assigned)")
    parser_update.add_argument("--project", default=default_project, help="GCP Project ID")
    parser_update.add_argument("--location", default="global", help="Location (default: global)")
    parser_update.add_argument("--user-store", default="default_user_store", help="User Store ID (default: default_user_store)")
    parser_update.add_argument("--quota-project", help="GCP Project ID for quota/billing")

    # Batch Update command
    parser_batch = subparsers.add_parser('batch-update', help='Batch update user licenses')
    parser_batch.add_argument("input_file", help="JSON file containing the batch update requests")
    parser_batch.add_argument("--delete-unassigned", action="store_true", help="Delete licenses not present in the requests")
    parser_batch.add_argument("--update-mask", help="Field mask for updates (e.g., 'license_config,license_assignment_state')")
    parser_batch.add_argument("--project", default=default_project, help="GCP Project ID")
    parser_batch.add_argument("--location", default="global", help="Location (default: global)")
    parser_batch.add_argument("--user-store", default="default_user_store", help="User Store ID (default: default_user_store)")
    parser_batch.add_argument("--quota-project", help="GCP Project ID for quota/billing")

    args = parser.parse_args()

    if args.command == 'list':
        list_user_licenses(args.project, args.location, args.user_store, args.quota_project, args.format, args.output)

    elif args.command == 'get':
        get_user_license(args.project, args.location, args.user_store, args.quota_project, args.user_principal)
    
    elif args.command == 'update':
        user_lic = {
            "userPrincipal": args.user_principal,
            "licenseAssignmentState": args.state
        }
        mask = "license_assignment_state"
        if args.state == 'UNASSIGNED':
            user_lic["licenseConfig"] = ""
            mask += ",license_config"
        elif args.config:
            user_lic["licenseConfig"] = args.config
            mask += ",license_config"
        
        batch_update_licenses(args.project, args.location, args.user_store, [user_lic], args.quota_project, update_mask=mask)

    elif args.command == 'batch-update':
        try:
            with open(args.input_file, 'r') as f:
                data = json.load(f)
                # We expect a list of userLicense objects
                if isinstance(data, list):
                    user_lics = data
                elif isinstance(data, dict):
                    # Handle cases where it's already wrapped in inlineSource or requests
                    if "inlineSource" in data and "userLicenses" in data["inlineSource"]:
                        user_lics = data["inlineSource"]["userLicenses"]
                    elif "requests" in data:
                        user_lics = data["requests"]
                    else:
                        print("Error: Invalid JSON structure.")
                        sys.exit(1)
                else:
                    print("Error: Invalid JSON format.")
                    sys.exit(1)
            batch_update_licenses(args.project, args.location, args.user_store, user_lics, args.quota_project, args.delete_unassigned, update_mask=args.update_mask)
        except Exception as e:
            print(f"Error: {e}")

    else:
        parser.print_help()
