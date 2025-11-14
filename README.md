Azure Data Studio to VS Code Connection Migrator
A simple Python script to migrate database connections from Azure Data Studio's settings.json to the format required by the VS Code MSSQL extension's settings.json.

📜 Purpose
Azure Data Studio (ADS) and the VS Code MSSQL extension store connection settings in slightly different JSON formats. If you are transitioning from ADS to using VS Code as your primary SQL IDE, this script automates the process of transferring your saved connections, including their group assignments, saving you from manually recreating each one.

⚠️ Important Prerequisites
Before you run this script, please ensure you have the following:

Python 3: The script is written in Python 3. You must have it installed on your system.

Source & Target Files: You need:

Your Azure Data Studio settings.json file (the source).

Your VS Code settings.json file (the target).

Connection Groups MUST Be Pre-created

This script does not create new connection groups in VS Code.

It works by mapping your old groups to your new groups using the group name (e.g., "SLTS", "OTDI", "ROOT").

You must manually create your connection groups in VS Code first. If a connection in the source file belongs to a group named "SLTS", you must have a group also named "SLTS" in VS Code for the script to map it correctly.

🚀 How to Use
Backup Your Files: Before you begin, make a backup copy of your VS Code settings.json file. This script overwrites the target file, so it's crucial to have a backup in case something goes wrong.

Run the Script: Open a terminal or command prompt, navigate to the directory where you saved migrate_settings.py, and run it:

Bash

python migrate_settings.py
Enter File Paths: The script will prompt you for two pieces of information:

Source File: Enter the full path to your Azure Data Studio settings.json file.

Target File: Enter the full path to your VS Code settings.json file.

Example (Windows):

Enter the path to the source (Azure Data Studio) JSON file: C:\Users\YourUser\AppData\Roaming\azuredatastudio\User\settings.json
Enter the path to the target (VS Code) JSON file: C:\Users\YourUser\AppData\Roaming\Code\User\settings.json
(Note: Paths will differ on macOS and Linux.)

Done! The script will read the source, transform the connections, and merge them into your target file. It will then print a success message showing how many connections were migrated.

⚙️ How It Works
Loads Data: Reads the source (ADS) and target (VS Code) JSON files.

Maps Groups: It finds the datasource.connectionGroups (Source) and mssql.connectionGroups (Target) and creates a translation map by matching the name of each group.

Processes Connections: It iterates through each connection in datasource.connections (Source).

Avoids Duplicates: It checks the id of each source connection. If a connection with that same id already exists in the target mssql.connections list, it skips it. This makes the script safe to run multiple times.

Transforms Settings: For each new connection, it maps the ADS format to the VS Code format:

options.connectionName -> profileName

options.server -> server

options.encrypt ("true") -> encrypt ("Mandatory")

options.trustServerCertificate ("true") -> trustServerCertificate (true)

...and so on.

Assigns Group: It uses the group map from Step 2 to assign the connection to the correct groupId in the target file.

Saves File: The script writes the updated data (including all your old VS Code settings plus the new connections) back to the target settings.json file.