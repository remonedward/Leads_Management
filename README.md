# Auto Leads - Leads Management System

A desktop application for managing leads and interactions, built with Python and PyQt5.

## Features

- **Dashboard**: Overview of your leads and database status.
- **Leads Management**:
    - Import leads from CSV files.
    - Manually add leads with any number of custom fields.
    - Inline editing of lead data in a table.
    - Automatic handling of 'id' conflicts from external CSVs.
- **Interaction Tracking**:
    - Log interactions (e.g., calls, emails) for each lead.
    - Store custom results and detailed notes.
- **Reports & Export**:
    - Filter interactions by date.
    - Export interaction reports to Excel.
- **Data Explorer**:
    - View and edit all database tables directly.
    - Add new custom fields (columns) to tables dynamically.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Leads_Management.git
   cd Leads_Management
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main_window.py
```

### Tips
- **CSV Import**: When importing a CSV, columns are automatically mapped. If the CSV has an `id` column, it will be renamed to `external_id` to prevent conflict with the system's internal ID.
- **Inline Editing**: Double-click any cell in the leads table or data explorer to edit it. Changes are saved automatically to the database.
- **Custom Fields**: You can add new fields to your leads or interactions through the 'Data Explorer' tab using the 'Add New Field' button.

## Architecture

- `main_window.py`: The main GUI application logic.
- `db_manager.py`: Handles all database operations using SQLite.
- `style.py`: Contains the custom QSS (Qt Style Sheets) for a modern UI.
- `leads_database.db`: The SQLite database file (created automatically on first run).

## Author

Developed by >>REMO_OX<<
