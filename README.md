# University of Michigan LSA Course Guide Class info Scraper
 An unofficial api to the University of Michigan's LSA Course Guide Class Information
 
 # Requirments
You must install python3 and the following python libraries to run the code 
 - python3.x go to https://python.org/downloads to downlaod and install python3
 - smtplib python module https://pypi.org/project/secure-smtplib/
 - requests python modeul https://pypi.org/project/requests/
 - BeautifulSoup4 python module https://pypi.org/project/beautifulsoup4/
 
 # Getting started
Once you have python3 and the libraries you can run the code as long as you don't want to send yourself an email.
If you do wish to receive emails from the bot you must:
- create or use an existing gmail account (I recommend getting a new account because of step 2)
- Turn on less secure apps (you must do this otherwise the smtplib cannot use your email) more info: https://support.google.com/accounts/answer/6010255?hl=en
- edit the credentials in the login.csv and add the file path of the login.csv to the sendEmail.py

