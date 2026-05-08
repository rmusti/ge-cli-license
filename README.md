# Gemini Enterprise License CLI (Discovery Engine)

This CLI tool manages user licenses for the Discovery Engine API (Vertex AI Agent Builder). It is designed to handle large-scale environments (800+ users) by implementing automatic pagination and batch chunking.

## 🚀 Quick Start

Ensure your `.env` file contains your `PROJECT_ID`.

```bash
chmod +x ge_cli_license.sh
```

---

## 📋 Commands & Usage

### 1. Listing Users (`list`)
Retrieves all assigned and unassigned licenses in the project. Supports automatic pagination for large datasets.

**Options:**
* `--format`: `table` (default), `json`, or `csv`.
* `--output`: Path to save the results.

**Examples:**
```bash
# View in terminal
./ge_cli_license.sh list

# Export to CSV (for Excel/Google Sheets)
./ge_cli_license.sh list --format csv --output all_users.csv

# Export to JSON (ready for batch-update reuse)
./ge_cli_license.sh list --format json --output all_users.json
```

---

### 2. Single User Update (`update`)
Add or modify a single user's license status.

**⚠️ CRITICAL:** You must provide `--config` when assigning a license to a new user to avoid the `NO_LICENSE` state.

**Examples:**
```bash
# Assign license (Correct way)
./ge_cli_license.sh update user@example.com --state ASSIGNED --config "projects/YOUR_PROJECT/locations/global/licenseConfigs/internal_only_agent_space"

# Revoke/Unassign license
./ge_cli_license.sh update user@example.com --state UNASSIGNED
```

---

### 3. Bulk Batch Update (`batch-update`)
Update hundreds of users at once using a JSON file. The tool automatically splits the file into batches of 100 to stay within API limits.

**Options:**
* `--delete-unassigned`: **Sync Mode**. If used, any user NOT in your JSON file will have their license deleted.

**Examples:**
```bash
# Standard Update (Updates users in file, leaves others alone)
./ge_cli_license.sh batch-update my_users.json

# Full Sync (Makes the system match your file EXACTLY)
./ge_cli_license.sh batch-update my_users.json --delete-unassigned
```

---

### 4. Get User Details (`get`)
Fetches the complete raw JSON data for a specific user.

```bash
./ge_cli_license.sh get user@example.com
```

---

### 5. Developer/API Reference (`--curl-only`)
Displays the exact raw `curl` commands with placeholders.

```bash
./ge_cli_license.sh --curl-only
```

---

## 🛠 Features & Advanced Logic

### 💡 The `NO_LICENSE` State
If a user shows as `NO_LICENSE` in the list, it means they are `ASSIGNED` in name but lack a valid `licenseConfig`.
**Fix:** Run the `update` command again for that user and include the `--config` parameter.

### 📄 Output Formats
* **CSV**: Generates a flat file with headers: `userPrincipal`, `licenseAssignmentState`, `licenseConfig`, `createTime`, `updateTime`, `lastLoginTime`.
* **JSON**: Generates a list of objects that can be used directly as input for the `batch-update` command.

### ⚡ Scaling Logic
* **Pagination**: The `list` command automatically detects the `nextPageToken` and continues calling the API until all users are retrieved.
* **Batch Chunking**: The `batch-update` command splits your input list into groups of 100 and processes them sequentially to avoid "Payload Too Large" errors.

### 🔒 Field Masking
The tool uses `updateMask` internally during updates. This ensures that if you only provide the `state`, other fields (like the user's creation time) are preserved and not overwritten with null values.
