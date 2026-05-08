#!/bin/bash

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

# Load .env if it exists
if [ -f .env ]; then
  source .env
fi

# Function to display curl examples
show_curl_examples() {
    echo "--- Raw Curl Examples ---"
    echo "1. List Licenses:"
    echo "   curl -X GET -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
    echo "        -H \"X-Goog-User-Project: \${PROJECT_ID}\" \\"
    echo "        \"https://discoveryengine.googleapis.com/v1/projects/\${PROJECT_ID}/locations/global/userStores/default_user_store/userLicenses\""
    echo ""
    echo "2. Get License for a User:"
    echo "   curl -X GET -H \"Authorization: Bearer \$(gcloud auth print-access-token)\" \\"
    echo "        -H \"X-Goog-User-Project: \${PROJECT_ID}\" \\"
    echo "        \"https://discoveryengine.googleapis.com/v1/projects/\${PROJECT_ID}/locations/global/userStores/default_user_store/userLicenses/\${USER_ID}\""
    echo "--------------------------"
}

if [ "$1" == "--curl-only" ]; then
    show_curl_examples
    exit 0
fi

# Run the Python script from the venv
if [ -d "venv" ]; then
    ./venv/bin/python ge_cli_license.py "$@"
else
    python3 ge_cli_license.py "$@"
fi
