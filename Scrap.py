"""
scrape class information from LSA Course Guide.
Can be used as a general API for information of classes.
I use it to let me know if Restricted seats change
so like enrollment management and Y1, Y2, Y3, Y4 reserved seats.
Check out how the code works and how you can use it at
https://github.com/john-trager/
@author John Trager 6-29-20 -> 7-1-20
"""

import datetime
import time
import requests
from bs4 import BeautifulSoup
import send_email

class Scrap:
    """
    Scrap object used to scrape an LSA course from LSA course guide
    Simply assign a url to the object call load_data and parse_data
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, url=""):
        self.url = url
        #used to store restricted_seats when checking if there was a change in the restricted seats
        self.buffer = []

        #lists to hold data#
        self.first_table = []
        self.all_tables = []
        self.temp = []
        self.temp2 = []
        self.temp3 = []

        #hold parsed/seperated data from self.all_tables
        self.class_num = [] #int
        self.class_open = [] #bool
        self.open_seat_num = [] #the number of open seats int
        self.section = [] #section number int
        self.class_type = [] #string of class type: (sem), (dis), or (lec)
        self.restricted_seats = [] #list of lists of restricted seats

        self.enroll_management = 0
        self.y_1 = 0
        self.y_2 = 0
        self.y_3 = 0
        self.y_4 = 0

        self.page = None
        self.soup = None
        self.table = None
        self.table_2 = None
        self.r_seats = []

    def set_url(self,url):
        """
        sets the url for the Scrap object
        """
        self.url = url

    def load_data(self):
        """
        requests html (form the self.url),
        parses the html for what we want (class_="col-md-1" and class_="col-md-2")
        parses that html into a list of lists of lists ...
        TODO: add parsing support for class_="col-md-4" for time of class
        """
        #requests page
        self.page = requests.get(self.url, headers={'User-Agent':"Mozilla/5.0"})

        #beutifulsoup parser (holds page html)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        #search preferences for scrape
        self.table = self.soup.find_all("div", class_="col-md-1")

        self.table_2 = self.soup.find_all("div", class_="col-md-2")

        #lists to hold data#
        self.first_table = []
        self.all_tables = []
        self.temp = []
        self.temp2 = []
        self.temp3 = []

        #hold parsed/seperated data from self.all_tables
        self.class_num = [] #int
        self.class_open = [] #bool
        self.open_seat_num = [] #the number of open seats int
        self.section = [] #section number int
        self.class_type = [] #string of class type: (sem), (dis), or (lec)
        self.restricted_seats = [] #list of lists of restricted seats

        #gets col-md-1 rows
        if len(self.table) > 0:

            for i in range(1,len(self.table)):
                try:
                    if i != 0 and (i) % 6 == 0:
                        self.first_table.append(self.temp)
                        #print("Added")
                        self.temp = []
                        #print("Temp: reset")

                    self.temp.append(self.table[i].text.split())

                    if i == len(self.table)-1:
                        self.first_table.append(self.temp)
                        #print("Added END")
                except (IndexError, ValueError) as error:
                    self.first_table.append("")
                    print("ERROR: no text " + str(error))

            self.all_tables.append(self.first_table)

        #gets col-md-2 rows
        for i in range(1,len(self.table_2)):
            self.temp3 = []
            table_rows = self.table_2[i].find_all('tr')
            #row -> tr td -> t_d
            for row in table_rows:
                t_d = row.find_all('td')
                row = [x.text for x in t_d]
                self.temp3.append(row)

            self.temp2.append(self.temp3)

        # print(self.temp2)
        # add temp2 (col-md-2) to all_tables in
        # corresponding sub arrays (adding open restricted seats)
        for j in range(1, len(self.all_tables[0])):
            self.all_tables[0][j].append(self.temp2[j-1])

    def parse_data(self):
        """
        Takes the data from self.all_tables and separates it into categorized lists
        (such as the class number, how many seats are open, etc...)
        Note: First call load_data before parsing data
        """

        for i in range(1, len(self.all_tables[0])):
            self.class_num.append(int(self.all_tables[0][i][2][2]))
            self.class_open.append(self.all_tables[0][i][3][2])
            self.open_seat_num.append(int(self.all_tables[0][i][4][2]))
            self.section.append(int(self.all_tables[0][i][0][1]))
            self.class_type.append(self.all_tables[0][i][0][2])
            self.restricted_seats.append(self.all_tables[0][i][6])

    def get_restricted(self,panel):
        """
        :Input: panel: the section/panel of the class starting
        from 0 to the n-1 number of sections on the page.
        Takes list of self.restricted_seats of the corresponding panel and
        parses to figure out how many seats are reserved for:
        -Enrollment Management
        -Y1 ,Y2, Y3, Y4 (certain year students)
        @return: returns the number of seats reserved in a set:
        (# Enroll Management, # Y1, # Y2, # Y3, # Y4)
        todo: fix edge case of "Y1 or Y2" combos
        """

        for i in range(len(self.restricted_seats[panel])):
            if len(self.restricted_seats[panel][i]) == 2:
                if "Y1" in str(self.restricted_seats[panel][i][1]).upper():
                    self.y_1 += int(self.restricted_seats[panel][i][0])
                elif "Enrollment" in self.restricted_seats[panel][i][1].strip():
                    self.enroll_management += int(self.restricted_seats[panel][i][0])
                elif "Y2" in str(self.restricted_seats[panel][i][1]).upper():
                    self.y_2 += int(self.restricted_seats[panel][i][0])
                elif "Y3" in str(self.restricted_seats[panel][i][1]).upper():
                    self.y_3 += int(self.restricted_seats[panel][i][0])
                elif "Y4" in str(self.restricted_seats[panel][i][1]).upper():
                    self.y_4 += int(self.restricted_seats[panel][i][0])

        return self.enroll_management, self.y_1, self.y_2, self.y_3, self.y_4

    def get_all_restricted(self):
        """
        returns list of sets of (Enrollment Management, Y1, Y2, Y3, Y4) for all panels/sections
        """
        self.r_seats = []
        for i in range(len(self.restricted_seats)):
            self.r_seats.append(self.get_restricted(i))
        return self.r_seats

    def get_r_seats_change(self):
        """
        Returns bool if restricted seats changed any values
        Sends Email to specified email if value changed
        """

        self.buffer.append(self.get_all_restricted())

        if len(self.buffer) > 2:
            self.buffer.pop(0)

        if len(self.buffer) > 1:
            #if a change in the bugger occurred
            if self.buffer[0] != self.buffer[1]:
                send_email.send_email(subject="UMich Class Update",
                body="A class has changed at: \n" + str(self.url) +
                "\n\nDate Time Occurred: " + str(datetime.datetime.now()) +
                "\n\nClass Number: " + str(self.class_num)+ "\n\nValue changed: " +
                str(self.buffer[0]) + " to " + str(self.buffer[1]))
                return True
        return False


if __name__ == "__main__":
    C = 0

    #put URLs from LSA course guide of classes you want to monitor here
    urls = [
    "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310PHIL183002&termArray=f_20_2310",
    "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310CLCIV120003&termArray=f_20_2310",
    "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310COMM159001&termArray=f_20_2310",
    "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310COMM159001&termArray=f_20_2310"]

    #creates Scrap object for url in URLs
    watchlist = [Scrap() for i in range(len(urls))]

    #set urls to corresponding Scrap object in watchlist
    for idx, class_ in enumerate(watchlist):
        class_.set_url(urls[idx])

    #heres where the main operations to the classes are done/checked
    while True:
        for class_ in watchlist:

            #load in data (send request)
            class_.load_data()
            #parse the data
            class_.parse_data()
            #check if restricted seats changed
            #and send email if it did
            class_.get_r_seats_change()

        #print to terminal every cycle so I know its working
        print("round " + str(C))
        C += 1
        #wait 60 seconds between every cycle to avoid getting blocked from website (403 error)
        time.sleep(60)
