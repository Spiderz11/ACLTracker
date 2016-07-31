# ACLTracker
This is just a small Python 3.4 app that Connects, logs, and tracks ACL Rules for usage. There are several paid apps out there that handle this function but we are moving to a config management solution that does not provide this function. The main function of this app is to pull data off and store it in a MySQL DB to pull stats from later. This should allow one to see when rules are not being used after an extended amount of time and put in queue to remove them. 

Functions of ACLTracker:
  1.	Connect to Cisco device and handle basic commands input and buffer output. Currently working from ASA 5000+. Commands are kept to session only and show commands.
  2.	Take buffer output and sort all ACLs and ACL Brief Hex output.
  3.	Store sorted output in MySQL. Checking for duplicates and changes in hit dates.

Imported modules:
  1.	Paramiko – SSH connectivity handler for connecting to devices.
  2.	Mysql.connector – MySQL DB connection

Versions:
  1.	Python: 3.4
  2.	Mysql: 5.7.9


