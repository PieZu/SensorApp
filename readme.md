A flask app for the storage and retrieval of sensor data.
Includes apis for the sensor to log data to, and a user-facing website that allows filtering, visualisation and csv extraction of the logged data.  

  

# setup

In order to initialise the app, follow these steps:
1. Clone this git repository
2. Make a file named config.py
	- Copy from the template in config.example.py
	- Set the secret key, this is solely used for securing encryption so make it random
3. Make a file in the `user` folder named config.py
	- Copy from the config.example.py in the same folder
	- Set the default user key to whatever you want the first (and most administrative) user's password to be
 4. If required, edit the config.py in the `database` folder
	- Set the DATABASE_PATH to adjust where the database file will be stored
    - Set DUMMY_DATA_AMOUNT to the number of desired fake/generated entries in the database (for demonstration uses set this as high as needed, and for production uses set this to 0)
 5. Ensure you have installed all dependent libraries in [requirements.txt](requirements.txt)
 6. Launch the app by running python app.py
