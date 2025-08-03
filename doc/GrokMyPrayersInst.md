1. Project Overview:
     - Purpose: The purpose of this application is to manage prayer sessions for a person desiring to connect with God on a daily or ongoing basis. It provides the context for praying (based on the Lord's Prayer), creates and stores new prayers, and presents previously stored prayers for additional prayer. It allows previously stored prayers to be marked as answered.
     - This is basically a purpose-specific CRUD application. The main object is: Prayer. There are several support objects like Category.
     - Language: Python
     - Architecture: The application follows the MVC pattern, with:
          - Model: Defined in `db_manager.py` (data management and database interactions) and `mpo_model.py` (core business entities and logic, such as data structures and business rules).
          - View: Defined in `ui_manager.py` (user interface components and presentation logic).
          - Controller: Defined in `app_controller.py` (handles user input, coordinates between Model and View).
         - Shared Logic: `mpo_model.py` contains business entities and logic shared across the MVC components.

2. Development Environment:
   - IDE: PyCharm 2025.1.3.1 (Community Edition)
   - Windows operating system.
   - Python Version: 3.11
   - Dependencies: TBD (List required libraries or frameworks (e.g., `tkinter` for the UI, `sqlalchemy` for the database, etc.). If none are specified yet, include a note to document dependencies in a `requirements.txt` file.)
   - Setup Instructions:
     - Install PyCharm (Community or Professional edition).
     - Ensure Python is installed and configured in PyCharm.
     - Clone the project repository (if using version control) or create the project structure with the four key files: `db_manager.py`, `ui_manager.py`, `app_controller.py`, `mpo_model.py`.
     - Install dependencies using `pip install -r requirements.txt` (if applicable).

3. File Structure:
   - `mpo_model.py`: Defines core business entities (e.g., classes, data structures) and business rules (specific logic like calculations or validations shared across the application. (backup: https://drive.google.com/file/d/15HzcKOmGFneeFBAoCza5oKBPtWxTbDrJ/view?usp=sharing)
   - `db_manager.py`: Implements the Model component, handling database operations (e.g., CRUD operations,). Example: Functions to query or update a database using an ORM or raw SQL. (backup: https://drive.google.com/file/d/1f38au2Je2a4PZUhpGLKO9Djl89ypjCRV/view?usp=sharing)
   - `ui_manager.py`: Implements the View component, managing the user interface (e.g., GUI elements via `tkinter`, command-line interface, or other display logic). (backup: https://drive.google.com/file/d/1DJfnsSqHRUeR6W0CaE4HbButfe_aZB0C/view?usp=sharing) 
   - `app_controller.py`: Implements the Controller component, coordinating user inputs, updating the Model, and refreshing the View. (backup: https://drive.google.com/file/d/1DXM6uduXtse3Eg7KglE_4z96KaL18LpU/view?usp=drive_link)
   - Link to Google Drive main directory for my_prayers_project (project root): https://drive.google.com/drive/folders/1CXYdNXyIPJjV6pEe6wuwM-yAJPuLr6kb?usp=sharing
     - Directory Structure: 
       - Source code (and default location for all project files): /src
       - Diagrams: /diagrams
       - Possible future directories:
         - doc/
         - config/
         -

4. Running the Application:
   - Entry Point: Execute `app_controller.py`.
   - Example Command: `python app_controller.py` in the project directory via PyCharm’s terminal or command prompt.
   - Configuration: TBD (Note any configuration files (e.g., database credentials, environment variables) needed for the application to run.)

5. Development Guidelines:
   - Coding Standards: Follow Python PEP 8 for style. Use clear, descriptive variable names and include docstrings for functions and classes.
   - When making changes to the source code, retain all comments.
   - Version Control: Git.
   - Testing: TBD (If applicable, include instructions for running tests; e.g., using `unittest` or `pytest`).
   - Documentation: Maintain a `README.md` with setup, usage, and contribution instructions.
   - 

6. Version Control:
   - PyCharm GUI for Git operations:
     - Commit: Ctrl+K to open the Commit dialog, select files, and commit.
     - Pull/Push: Use the VCS > Git menu or the Git toolbar.
     - View History: Right-click a file in the Project view and select Git > Show History to verify the latest changes.
   - Git commands:
     - git add db_manager.py ui_manager.py app_controller.py mpo_model.py
     - git commit -m "Update MVC files for Grok review"
     - git push origin main
   - Git repository: https://github.com/joscthomas/my_prayers/tree/main/src 
   - Gir repository shared access: https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/ui_manager.py.

7. Troubleshooting: TBD
   - Common issues (e.g., missing dependencies, database connection errors).
   - Instructions for checking logs or debugging in PyCharm.

8. Future Enhancements: (possible)
   - Changing the user interface technology to some GUI.
   - Changing the database technology.

9. Learning Persona Profile: these are the characteristics of me (a programmer)
    - I grew up as a procedural programmer. I'm pretty good at it.
    - I've learned about object-oriented design and programming. I am pretty familiar with the concepts, but have no experience coding this way. 
    - I've done a little Python programming, but am not an expert and am still learning basic concepts. 
    - I like to learn mostly by reading. Reading lets me skip around to the part I am interested in. I find that videos often move too slowly, and I feel captive to them, unless they are well produced. 

10. Code Walkthrough Roles: This describes the rules for code walkthroughs and tutorial sessions
    - You and I will conduct code walkthroughs as a way for me to learn about object-oriented design and programming. 
    - You are the expert. I am still learning. 
    - When we walk through code, ask me questions about my understanding of the code that we are looking at. 

11. Walk-Through Session Workflow
    - Before WT Session: I get the latest commit hash from Git (e.g., git log -1 --pretty=%H in PyCharm’s terminal or Git panel) and push changes to https://github.com/joscthomas/my_prayers/ (git push origin main).
    - Start WT Session: I specify files (e.g., ui_manager.py) and focus (e.g., “OOP in View component”).
    - You ask, “What’s the latest commit hash for main?” to confirm access to https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/.
    - Confirm Git Access: I provide the commit hash. You verify files (e.g., https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/ui_manager.py). If inaccessible, I copy-paste contents as a fallback.
    - Structured WT Session:
      - Overview: Summarize file’s MVC role (e.g., “ui_manager.py handles View”).
      - Snippet Display: Show relevant code from GitHub raw URLs.
      - Questions: Ask 1–2 questions (e.g., “How does UIManager.display_menu work?”).
      - OOP Explanation: Compare to procedural concepts, tailored to your background.
    - Action Items: List immediate changes or To-Do List entries.
      - Make or Defer Changes:
        - Immediate: You apply changes in PyCharm (I provide snippets).
        - Deferred: I add to doc/todo.md (ID, name, type, priority, description).
    - End Session:
      - I commit (Ctrl+K, e.g., “WT updates for ui_manager.py”) and push (git push origin main).
      - You summarize and update doc/todo.md.

12. Td Do List: to keep track of design and code base fixes that result from walkthroughs and refactoring. 
    - File: doc/todo.md 
    - The properties for each todo item: unique_id, name, type, priority, description. 
    - At the end of each walk-through session, we will decide which fixes we want to implement as part of the session and which fixes we want to keep on the project todo list for addressing later.

13. Unit Testing
    - Coming soon. 

14. Continuous Integration
    - Coming soon.