import json
import os

def migrate_connections():
    """
    Prompts for source and target JSON files, then migrates Azure Data Studio
    connection settings to the VS Code (mssql extension) format.
    """
    
    # 1. Get file paths from the user
    try:
        source_path = input("Enter the path to the source (Azure Data Studio) JSON file: ")
        target_path = input("Enter the path to the target (VS Code) JSON file: ")

        # Validate paths
        if not os.path.exists(source_path):
            print(f"Error: Source file not found at '{source_path}'")
            return
            
        if not os.path.exists(target_path):
            print(f"Error: Target file not found at '{target_path}'")
            print("Please ensure the target settings.json file exists.")
            return

        # 2. Read the source and target files
        with open(source_path, 'r') as f:
            source_data = json.load(f)
            
        with open(target_path, 'r') as f:
            target_data = json.load(f)

    except FileNotFoundError as e:
        print(f"Error: File not found. {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON. Check file for syntax errors. {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during file loading: {e}")
        return

    # 3. Create mapping for connection groups
    # We need to map the source group ID to the target group ID
    # by using the group 'name' as the common link.
    
    try:
        source_groups = source_data.get('datasource.connectionGroups', [])
        target_groups = target_data.get('mssql.connectionGroups', [])

        # Map source group ID -> group Name
        source_id_to_name = {g['id']: g['name'] for g in source_groups}
        
        # Map group Name -> target group ID
        target_name_to_id = {g['name']: g['id'] for g in target_groups}

        if not target_name_to_id:
            print("Warning: No 'mssql.connectionGroups' found in target file.")
            
    except Exception as e:
        print(f"Error processing connection groups: {e}")
        return

    # 4. Process and migrate connections
    source_connections = source_data.get('datasource.connections', [])
    
    # Ensure the target list exists
    if 'mssql.connections' not in target_data:
        target_data['mssql.connections'] = []

    # Get existing connection IDs from target to avoid duplicates
    existing_target_ids = {c.get('id') for c in target_data['mssql.connections']}
    
    migrated_count = 0
    skipped_count = 0

    for conn in source_connections:
        conn_id = conn.get('id')
        
        # Skip if a connection with this ID already exists in the target
        if conn_id in existing_target_ids:
            skipped_count += 1
            continue

        opts = conn.get('options', {})
        if not opts:
            print(f"Skipping connection {conn_id}: No 'options' field found.")
            skipped_count += 1
            continue
            
        # Find the correct target group ID
        target_group_id = None
        
        # Prioritize the 'groupId' from within the 'options' object
        source_group_id = opts.get('groupId')
        
        # Fallback to the outer 'groupId' if 'options.groupId' is missing
        if not source_group_id:
            source_group_id = conn.get('groupId')
            
        if source_group_id:
            group_name = source_id_to_name.get(source_group_id)
            if group_name:
                target_group_id = target_name_to_id.get(group_name)

        # Map source 'encrypt' string to target 'encrypt' setting
        encrypt_setting = "Optional"
        if opts.get('encrypt', '').lower() == 'true':
            encrypt_setting = "Mandatory"
            
        # Convert source 'trustServerCertificate' string to target boolean
        trust_cert_setting = opts.get('trustServerCertificate', '').lower() == 'true'

        # Create the new connection entry in VS Code format
        new_conn = {
            "id": conn_id,
            "server": opts.get('server'),
            "database": opts.get('database'),
            "authenticationType": opts.get('authenticationType'),
            "user": opts.get('user'),
            "password": opts.get('password'),
            "profileName": opts.get('connectionName'),
            "groupId": target_group_id,
            
            # Add default values based on VS Code format
            "applicationName": "vscode-mssql",
            "encrypt": encrypt_setting,
            "trustServerCertificate": trust_cert_setting,
            "connectTimeout": 30,
            "commandTimeout": 30,
            "applicationIntent": "ReadWrite"
        }
        
        # Add the new connection to the target list
        target_data['mssql.connections'].append(new_conn)
        migrated_count += 1

    # 5. Write the updated data back to the target file
    try:
        with open(target_path, 'w') as f:
            json.dump(target_data, f, indent=4)
            
        print("\n--- Migration Complete ---")
        print(f"Successfully migrated {migrated_count} new connection(s).")
        print(f"Skipped {skipped_count} connection(s) (already exist in target).")
        print(f"Your target file '{target_path}' has been updated.")

    except Exception as e:
        print(f"Error writing to target file '{target_path}': {e}")


if __name__ == "__main__":
    migrate_connections()