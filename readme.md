This app manages a list of prayers. Its user interface provides the ability 
to conduct a prayer session.


Here is the flow upon running the app: 

    - Open a prayer session
        - Present welcome message to set the context and mood
            - click to proceed
        - Present a message inviting the user to worship Jesus
            - click to proceed
        - Present a message inviting the user to share their concerns
        with God
            - "Add Prayer" button initiates a dialog that adds a new prayer
            to the database 
            - Click button to add more prayers
            - Click to proceed
        - Retrieve a group of N prayers from the database
            -Use an algorithm to select the prayers
                -Algorithm chooses randomly, but weighted so most recent
                prayers are first
            - Repeat presenting prayers N at a time
                - Until clicking end button
        - Present a message of hope and encouragement
        - Present a closing message
        - End

Key Concepts:

    - PrayerSession : a period of prayer
    - PanelSet : a set of Panels to present on the computer display during a PrayerSession
    - 

Directory structure

    - mp_project : parent directory of my_prayers
        - src : contains Python source code for project
        - test : contains Python source code for automated testing of the main project
        - db : contains SQLite database

Configuration management

    - git status 
    - git add filename.py
    - git commit -m message
    - git push

To run a test: 

    - Delete objects.pkl in src

To generate UML class diagrams: 

    - open Windows Command window
    - cd C:\Users\jcthomas\Documents\JCT Documents\Python\my_prayers_project\src
    - pyreverse -o png -p MyPrayers .
    - move classes_MyPrayers.png, packages_MyPrayers.png to diagrams/
    - ![Class Diagram](diagrams/classes_PrayerApp.png)


Main module : my_prayers.py

		
Modeled after YouVersion's Pray Now function.