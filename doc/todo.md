My Prayers Project To-Do List

- T001: Add Type Hints for UML Class Diagram
  - Type: Enhancement
  - Priority: Medium
  - Status:
  - Description: Add type hints using Python’s typing module (e.g., List, Optional) to instance variables and method parameters/return types to clarify relationships for PyCharm’s UML diagram. Ensure proper imports, preserve all comments, and follow PEP 8. The goal is to make associations (e.g., AppController → UIManager), dependencies, and compositions (e.g., Prayer → Category) visible in the UML diagram.


- TD002: Grok File Retrieval Error
  - Type: Bug
  - Priority: High
  - Status:
  - Description: Grok retrieves incorrect db_manager.py (63 lines, starts with import sqlite3) from https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/db_manager.py, despite the correct file having 376 lines. Recurred from August 2, 2025. Investigate potential caching, commit hash mismatch, or retrieval logic issues.


- T003: Test Data Directory
  - Type: Testing
  - Priority: Medium
  - Status:
  - Description: Verify data_file_path from params.json works with a custom directory.


- T004: Test Fallback Loading
  - Type: Testing
  - Priority: Medium
  - Status:
  - Description: Test loading from CSV/JSON when pickle file is missing.


- T005: Verify AppParams
  - Type: Code Update
  - Priority: High
  - Status:
  - Description: Confirm AppParams in mpo_model.py correctly defines data_file_path.


