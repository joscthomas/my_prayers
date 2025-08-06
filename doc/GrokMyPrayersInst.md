1. Project Overview:
     - Purpose: The purpose of this application is to manage prayer sessions for a person desiring to connect with God on a daily or ongoing basis. It provides the context for praying (based on the Lord's Prayer), creates and stores new prayers, and presents previously stored prayers for additional prayer. It allows previously stored prayers to be marked as answered.
     - This is a purpose-specific CRUD application. The main object is: Prayer. There are several support objects, such as Category.
     - Language: Python
     - Architecture: The application follows the Model-View-Controller (MVC) pattern.

2. Development Environment:
   - IDE: PyCharm 2025.1.3.1 (Community Edition)
   - Windows operating system.
   - Python Version: 3.11
   - Dependencies: TBD (List required libraries or frameworks (e.g., `tkinter` for the UI, `sqlalchemy` for the database, etc.). If none are specified yet, include a note to document dependencies in a `requirements.txt` file.)
   - Setup Instructions:
     - Install PyCharm (Community or Professional edition).
     - Ensure Python is installed and configured in PyCharm.
     - Clone the project repository (if using version control) or create the project file structure.
     - Install dependencies using `pip install -r requirements.txt` (if applicable).

3. File Structure:
   - `mpo_model.py`: Defines core business entities (e.g., classes, data structures) and business rules (specific logic like calculations or validations shared across the application.) 
   - `db_manager.py`: Implements the Model component of the MVC pattern, handling database operations (e.g., CRUD operations). 
   - `ui_manager.py`: Implements the View component of the MVC pattern, managing the user interface (e.g., GUI, command-line interface, or other display logic). 
   - `app_controller.py`: Implements the Controller component of the MVC pattern, coordinating user inputs, updating the Model, and refreshing the View.
   - Backup of project files for my_prayers_project: https://drive.google.com/drive/folders/1CXYdNXyIPJjV6pEe6wuwM-yAJPuLr6kb?usp=sharing
     - Directory Structure: 
       - Source code (and default location for all project files): /src
       - Diagrams: /diagrams
       - Possible future directories:
         - doc/
         - config/

4. Running the Application:
   - Entry Point: Execute `app_controller.py`.
   - Example Command: `python app_controller.py` in the project directory via PyCharm's terminal or command prompt.
   - Configuration: TBD (Note any configuration files (e.g., database credentials, environment variables) needed for the application to run.)

5. Development Guidelines:
   - Coding Standards: Follow Python PEP 8 for style. Use clear, descriptive variable names and include docstrings for functions and classes.
   - When making changes to the source code, retain all comments.
   - Version Control: Git.
   - Testing: TBD (If applicable, include instructions for running tests; e.g., using `unittest` or `pytest`).
   - Documentation: Maintain a `README.md` with setup, usage, and contribution instructions.

6. Version Control:
   - PyCharm GUI for Git operations:
     - Commit: Ctrl+K to open the Commit dialog, select files, and commit.
     - Pull/Push: Use the VCS > Git menu or the Git toolbar.
     - View History: Right-click a file in the Project view and select Git > Show History to verify the latest changes.
   - Git commands:
     - git add db_manager.py ui_manager.py app_controller.py mpo_model.py
     - git commit -m "Update MVC files for Grok review"
     - git push origin main
   - GitHub repository: https://github.com/joscthomas/my_prayers/tree/main/src 
   - GitHub repository shared access: https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/ui_manager.py.

7. Troubleshooting: TBD
   - Common issues (e.g., missing dependencies, database connection errors).
   - Instructions for checking logs or debugging in PyCharm.

8. Future Enhancements: (possible)
   - Changing the user interface technology to a GUI.
   - Changing the database technology.

9. Learning Persona Profile: these are the characteristics of me (a programmer)
    - I grew up as a procedural programmer. I'm pretty good at it.
    - I've learned about object-oriented design and programming. I am pretty familiar with the concepts, but have no experience coding this way. 
    - I've done a little Python programming, but am not an expert and am still learning basic concepts. 
    - I like to learn mostly by reading. Reading lets me skip around to the part I am interested in. I find that videos often move too slowly, and I feel captive to them, unless they are well-produced. 

10. Code Walkthrough Roles: This describes the rules for code walkthroughs and tutorial sessions.
    - You and I will conduct code walkthroughs as a way for me to learn about object-oriented design and programming. 
    - You are the expert. I am still learning. 
    - When we walk through code, ask me questions about my understanding of the code that we are looking at. 

11. Walk-Through Session Workflow
    - Get project files to work with using the ACTIVE Project File Retrieval method; by default, always use these files: mpo_model.py, app_controller.py, db_manager.py, ui_manager.py, todo.md
    - Structured WT Session:
      - Overview: Summarize file's MVC role (e.g., "ui_manager.py handles View").
      - Snippet Display: Show relevant code from GitHub raw URLs.
      - Questions: Ask 1–2 questions (e.g., "How does UIManager.display_menu work?").
      - OOP Explanation: Compare to procedural concepts, tailored to your background.
    - Action Items: List immediate changes or To-Do List entries.
      - Make or Defer Changes:
        - Immediate: You apply changes in PyCharm (I provide snippets).
        - Deferred: I add to doc/todo.md (ID, name, type, priority, description).
    - End Session:
      - I commit (Ctrl+K, e.g., "WT updates for ui_manager.py") and push (git push origin main).
      - You summarize and update doc/todo.md.

12. Project File Retrieval from GitHub Repository (INACTIVE; do not use this because of problems Grok has retrieving project files from GitHub repository)
    - Before WT Session: I ensure that the latest files are checked into GitHub and get the latest commit hash.
    - Start WT Session: I specify focus for the session (e.g., "OOP in View component").
    - Get GitHub hash: You ask, "What's the latest commit hash for main?" to confirm access to the GitHub repository.
    - Confirm Git Access: I provide the commit hash. You verify files (e.g., https://raw.githubusercontent.com/joscthomas/my_prayers/main/src/ui_manager.py). 
    - Confirm correct files: 
      - Never make assumptions about having the correct files. 
      - Always retrieve the files from the GitHub repository. 
      - Always tell me the number of lines in the file. 
      - Provide me with the opportunity to view the file you retrieved with the text-based Grok file edit icon (do not show inline and not with the GitHub URL). 
      - Pause to allow me to review the files you have retrieved and confirm they are correct before we proceed. 
    - Fallback for inaccessible files: If the files are inaccessible, I copy-paste contents as a fallback.

13. Project File Retrieval from File Attachment (ACTIVE; second choice behind retrieving project files from GitHub repository)
    - Start WT Session: I specify the files for the session by using the Grok attach file option for a conversation.  
    - Always tell me the number of lines in the file. 
    - Provide me with the opportunity to view the file you retrieved with the text-based Grok file edit icon (do not show inline and not with the GitHub URL). 
    - Pause to allow me to review the files you have retrieved and confirm they are correct before we proceed. 
    - Fallback for inaccessible files: If this method does not work, I copy-paste contents as a fallback.

14. Mode of Responding: describes how you are to respond when we are collaborating or having a conversation.
    - Keep your responses brief, summarizing in a sentence or two with no extra details. 
     - When presenting a list, present the items in the list with their titles only. Do not describe them.
    - I will ask if I want more details.
    - Keep responses concise, using 1-2 sentences per main point.
    - Use bullet points or numbered lists for clarity and brevity.
    - Include only titles or key terms in lists, avoiding extra descriptions unless requested.
    - Prioritize relevant information based on the query and project context.
    - Avoid technical jargon unless directly related to the question or walkthrough focus.
    - Always show files with the file edit icon. Never show files inline (code snippets of small files shown inline are okay). 
    - Never display or list code (unless presenting an example). Just show the file edit icon.
    - Do not provide Git commands unless I request them.

15. To Do List: to keep track of design and code base fixes that result from walkthroughs and refactoring. 
    - File: doc/todo.md 
    - The properties for each todo item: unique_id, name, type, priority (critical, high, medium, low), status (open, complete, deferred), description. 
    - At the end of each walk-through session, we will decide which fixes we want to implement as part of the session and which fixes we want to keep on the project to-do list for addressing later.
    - Always retrieve the latest version of todo.md from the GitHub repository and make it available for me to review using a file edit icon. 
    - When adding new todo items, append them to the current todo.md file. 
    - I will copy the todo.md file and add the updated version in the repository upon completion of our session.
    - Always provide the todo.md content in a plain text code block, which should retain all formatting, including dashes and indentation.

16. Unit Testing
    - Coming soon. 

17. Continuous Integration
    - Coming soon.