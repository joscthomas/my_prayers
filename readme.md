This app manages a list of prayers. Its user interface provides the ability 
to:

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
        - Retrieve a group of three prayers from the database
            -Use an algorithm to select the three prayers
                -Algorithm chooses randomly, but weighted so most recent
                prayers are first
            - Repeat presenting prayers three at a time
                - Until clicking end button
        - Present a message of hope and encouragement
        - Present a closing message
        - End

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


Main module : my_prayers.py

		
Modeled after YouVersion's Pray Now function.