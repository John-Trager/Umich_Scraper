# University of Michigan LSA Course Guide Class info Scraper
 An unofficial api to the University of Michigan's LSA Course Guide Class.
 The program can read and parse information about a class on lsa course guide and return information to you. The following are currently available attributes that can be accessed: 
 * Class Number
 * If the Class is Open or Closed
 * The amount of open seats left
 * The Section Number
 * The Class Type (such as seminar, lecture, discussion, or lab)
 * The Number of Restricted Seats be that for Enroll Management, Year 1, 2, 3, or 4 students
 
 # Requirements
You must install python3 and the following python libraries to run the code.
 - python3.x go to https://python.org/downloads to download and install python3
 - requests python module https://pypi.org/project/requests/
 - BeautifulSoup4 python module https://pypi.org/project/beautifulsoup4/
 If you have pip you can use the requirements.txt to easily install the required modules.
 
 # Getting started
Once you have python3 and the libraries you can run the code as long as you don't want to send yourself an email.
If you do wish to receive emails from the bot you must:
- create or use an existing gmail account (I recommend getting a new account because of step 2)
- Turn on less secure apps (you must do this otherwise the smtplib cannot use your email) more info: https://support.google.com/accounts/answer/6010255?hl=en
- edit the credentials in the login.csv and add the file path of the login.csv to the sendEmail.py

