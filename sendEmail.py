"""
send emails using smtplib
make sure you add a credentils/login csv file that has in this order:

sender/bot email without the @gmail.com portion (example: johdoe don't use johndoe@gmail.com), password to sender/bot email,
the email address you want to ewceive the automated emaisl from

also see example login file on github
example:
johndoe, password!, receiver@gmail.com

@author John Trager 7-1-20
"""
import smtplib
import csv

file_url = "PATH TO LOGIN FILE" # !!you must add the path to your login.csv and put the correct values into the file!!
debug = False

def sendEmail(email_receiver, subject, body):
    """
    :input: email_receiver: the email address to who the email is going to (string)
    :input: subject: the subject of the email (string)
    :input: body: the body of the email (string)
    """

    try:
        with open(file_url, 'r') as login:
            whole_text = csv.reader(login)
            items = next(whole_text)
            email_address = items[0]
            email_password = items[1]
            email_sender = items[2]
            print("Email: " + str(email_address) + '\n' + "pass: " + str(email_password) + '\nsend to: ' + str(email_sender)) if debug == True else None
    except Exception as e:
        print("\nError: parsing login file, make sure gmail less secure app is enabled \nException: " + str(e) + "\n")


    try:

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            #encrypt traffic
            smtp.starttls()
            #re identify connection with new encrytion
            smtp.ehlo()
            #login
            smtp.login(email_address, email_password)


            email_sender = email_receiver
            #email_sender = "autobot5067@gmail.com"
            subject = subject
            body = body

            msg = 'Subject: {}\n\n{}'.format(subject,body)

            #(sender,receiver,msg)
            smtp.sendmail(email_address, email_sender, msg)

            print("SENT")
    
    except Exception as e:
        print("Error: there was a problem sending the email make sure the email address is valid and\n body and subject line are strings and error free\n")
