import sendEmail
import requests
import datetime
import time
from bs4 import BeautifulSoup

"""
scrape class information from LSA Course Guide. Can be used as a general API for information of classes.
I use it to let me know if Restricted seats change so like enrollment management and Y1, Y2, Y3, Y4 reserved seats.
Check out how the code works and how you can use it at https://github.com/john-trager/
@author John Trager 6-29-20 -> 7-1-20
"""


class Scrap:
    """
    Scrap object used to scrape an LSA course from LSA course guide
    Simply assign a URL to the object call loadData and parseData 
    """

    def __init__(self, URL=""):
        self.URL = URL
        #used to store restrictedSeats when checking if there was a change in the restricted seats
        self.buffer = []

    def setURL(self,URL):
        """
        sets the URL for the Scrap object
        """
        self.URL = URL

    def loadData(self):
        """
        requests html (form the self.URL),
        parses the html for what we want (class_="col-md-1" and class_="col-md-2")
        parses that html into a list of lists of lists ...
        TODO: add parsing support for class_="col-md-4" for time of class
        """
        #requests page
        self.page = requests.get(self.URL, headers={'User-Agent':"Mozilla/5.0"})

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
        self.classNum = [] #int
        self.classOpen = [] #bool
        self.openSeatNum = [] #the number of open seats int
        self.section = [] #section number int
        self.classType = [] #string of class type: (sem), (dis), or (lec)
        self.restrictedSeats = [] #list of lists of restricted seats

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
                except:
                    self.first_table.append("")
                    print("ERROR: no text")

            self.all_tables.append(self.first_table)

        #gets col-md-2 rows
        for i in range(1,len(self.table_2)):
            self.temp3 = []
            table_rows = self.table_2[i].find_all('tr')

            for tr in table_rows:
                td = tr.find_all('td')
                row = [x.text for x in td]
                self.temp3.append(row)
            
            self.temp2.append(self.temp3)

        #print(self.temp2)
        #add temp2 (col-md-2) to all_tables in corresponding sub arrays (adding open restricted seats)
        for j in range(1, len(self.all_tables[0])):
            self.all_tables[0][j].append(self.temp2[j-1])

    def parseData(self):
        """
        Takes the data from self.all_tables and separates it into categorized lists
        (such as the class number, how many seats are open, etc...)
        Note: First call loadData before parsing data
        """

        for i in range(1, len(self.all_tables[0])):
            self.classNum.append(int(self.all_tables[0][i][2][2])) 
            self.classOpen.append(self.all_tables[0][i][3][2]) 
            self.openSeatNum.append(int(self.all_tables[0][i][4][2])) 
            self.section.append(int(self.all_tables[0][i][0][1])) 
            self.classType.append(self.all_tables[0][i][0][2])
            self.restrictedSeats.append(self.all_tables[0][i][6])

    def getRestricted(self,panel):
        """
        :Input: panel: the section/panel of the class starting from 0 to the n-1 number of sections on the page.
        Takes list of self.restrictedSeats of the corresponding panel and 
        parses to figure out how many seats are reserved for:
        -Enrollment Management
        -Y1 ,Y2, Y3, Y4 (certain year students)
        @return: returns the number of seats reserved in a set: (# Enroll Management, # Y1, # Y2, # Y3, # Y4)
        TODO: fix edge case of "Y1 or Y2" combos
        """
        self.em = 0
        self.y1 = 0
        self.y2 = 0
        self.y3 = 0
        self.y4 = 0
        for i in range(len(self.restrictedSeats[panel])):
              if len(self.restrictedSeats[panel][i]) == 2:
                     if "Y1" in str(self.restrictedSeats[panel][i][1]).upper():
                            self.y1 += int(self.restrictedSeats[panel][i][0])
                     elif "Enrollment" in self.restrictedSeats[panel][i][1].strip():
                            self.em += int(self.restrictedSeats[panel][i][0])
                     elif "Y2" in str(self.restrictedSeats[panel][i][1]).upper():
                            self.y2 += int(self.restrictedSeats[panel][i][0])
                     elif "Y3" in str(self.restrictedSeats[panel][i][1]).upper():
                            self.y3 += int(self.restrictedSeats[panel][i][0])
                     elif "Y4" in str(self.restrictedSeats[panel][i][1]).upper():
                            self.y4 += int(self.restrictedSeats[panel][i][0])
        
        return self.em, self.y1, self.y2, self.y3, self.y4

    def getAllRestricted(self):
        """
        returns list of sets of (Enrollment Management, Y1, Y2, Y3, Y4) for all panels/sections
        """
        self.r_seats = []
        for i in range(len(self.restrictedSeats)):
            self.r_seats.append(self.getRestricted(i))
        return self.r_seats

    def getRSeatsChange(self):
        """
        Returns bool if restricted seats changed any values
        Sends Email to specified email if value changed
        """

        self.buffer.append(self.getAllRestricted())
        
        if len(self.buffer) > 2:
            self.buffer.pop(0)

        if len(self.buffer) > 1:
            if self.buffer[0] == self.buffer[1]:
                return False
            else:
                sendEmail.sendEmail(subject="UMich Class Update",
                msg="A class has changed at: \n" + str(self.URL) + "\n\nDate Time Occurred: " + str(datetime.datetime.now()) +
                "\n\nClass Number: " + str(self.classNum)+ "\n\nValue changed: " + str(self.buffer[0]) + " to " + str(self.buffer[1]))
                return True
        else:
            return False


if __name__ == "__main__":
    c = 0

    #put URLs from LSA course guide of classes you want to monitor here
    urls = ["https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310PHIL183002&termArray=f_20_2310",
            "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310CLCIV120003&termArray=f_20_2310",
            "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310COMM159001&termArray=f_20_2310",
            "https://www.lsa.umich.edu/cg/cg_detail.aspx?content=2310COMM159001&termArray=f_20_2310"]

    #creates Scrap object for url in URLs
    watchlist = [Scrap() for i in range(len(urls))]

    #set urls to corresponding Scrap object in watchlist
    for idx, class_ in enumerate(watchlist):
        class_.setURL(urls[idx])

    #heres where the main operations to the classes are done/checked
    while True:
        for class_ in watchlist:
            
            #load in data (send request)
            class_.loadData()
            #parse the data
            class_.parseData()
            #check if restricted seats changed
            #and send email if it did
            class_.getRSeatsChange()
        
        #print to terminal every cycle so I know its working
        print("round " + str(c))
        c += 1
        #wait 60 seconds between every cycle to avoid getting blocked from website (403 error)
        time.sleep(60)
  