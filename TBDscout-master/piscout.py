import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from time import sleep
import ctypes
import requests
# from threading import Thread
import sqlite3 as sql
from event import CURRENT_EVENT
import gamespecific as game
import serverinfo
import json
import logging
import mysql.connector
import datetime

# PiScout is a means of collecting match data in a scantron-like format
# This program was designed to be easily configurable, and new sheets can be made rapidly
# The configuration for the sheets is done in a separate file (gamespecific.py)
# Cory Lynch 2015

SHADED_VAL = 45000

logging.basicConfig(
    filename = 'piscout.log',
    level=logging.DEBUG
)
logging.debug("\nStarting PiScout " + str(datetime.datetime.now()))

db_user = "root"
db_password = "root"
db_host = "127.0.0.1"
db_database = "data_" + CURRENT_EVENT

class PiScout:
    # Firstly, initializes the fields of a PiScout object
    # Then it starts the main loop of PiScout
    # Requires a function "processSheet" which contains the sheet configuration
    # Loops indefinitely and triggers a response whenever a new sheet is added
    def __init__(self):
        logging.debug("PiScout Init")
        try:
            print('PiScout Starting')
            logging.debug('PiScout Starting')
            self.sheet = None
            self.display = None
            self.matchData = dict(game.SCOUT_FIELDS)
            self.pitData = dict(game.PIT_SCOUT_FIELDS)
            self.labels = []
            self.type = 0
            self.shift = 0

            #Uses relative path to Sheets subdirectory where scans are stored
            f = set(os.listdir("Sheets_TBD"))
            logging.debug('About to loop')

            """
            # For debugging
            loop_max = 100
            i = 0
            """
            while True:
                sleep(0.25)
                files = set(os.listdir("Sheets_TBD")) #grabs all file names as a set
                added = files - f #check if any files were added
                for file in added:
                    if '.jpg' in file.lower() or '.png' in file.lower():

                        logging.debug('Found file ' + file)
                        logging.debug('Calling self.loadsheet')

                        retval = self.loadsheet("Sheets_TBD/" + file)
                        logging.debug('Return from self.loadsheet is %s \n', retval)

                        #If loading succeeds, process and add to the list of existing files, if the loading has a critical failure, add the file to the list. If the load has a temporary failure, retval is 0 and the file will be reprocessed on the next pass
                    if retval == 1:
                        logging.debug('Calling game.processSheet')
                        game.processSheet(self)
                        f.add(file)
                    elif retval == -1:
                        f.add(file)
                """
                # For debugging
                i += 1
                if i > loop_max:
                    break
                """
        except Exception as e:
            logging.error(e)
            raise

    # Loads a new scout sheet from an image
    # Processes the image and stores the result in self.sheet
    def loadsheet(self, imgpath, b=3, guess=False):
        logging.debug('Inside loadsheet')

        self.matchData = dict(game.SCOUT_FIELDS)
        self.pitData = dict(game.PIT_SCOUT_FIELDS)
        print('Loading a new sheet: ' + imgpath)
        
        #Sometimes the file has been created but the scanner has not yet finished writing to it. In these cases the resize will fail. Return 0 so the file will be reprocessed
        img = cv2.imread(imgpath)
        try:
            img = cv2.resize(img, (2456,3260))
        except:
            return 0
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # The first step is to figure out the four markers on the corners of the page
        # The next two lines will blur the image and extract the edges from the shapes
        blur = cv2.medianBlur(imgray, 2*b + 1)
        #cv2.imwrite('Output/' + imgpath[7:] + '.b' + str(b) + '.jpg', blur)
        retVal, edges = cv2.threshold(blur,200,255, cv2.THRESH_BINARY)
        #cv2.imwrite('Output/' + imgpath[7:] + '.thresh.jpg', edges)

        # Next, we use the edges to find the contours of the shapes
        # Once the contours are found, we use approxPolyDP to resolve the contours into polygon approximations
        # If the polygons have 4 sides and are relatively large, save the center coordinates in sq[]
        image, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        sq = []
        sqsize = []
        for cont in contours:
                poly = cv2.approxPolyDP(np.array(cont), 64, True)
                if len(poly) == 4 and cv2.contourArea(cont) > 4000:
                    xpos = 0; ypos = 0
                    for a in poly:
                        xpos += a[0][0]
                        ypos += a[0][1]
                    sq.append((int(xpos/4), int(ypos/4)))
                    sqsize.append(cv2.contourArea(cont))

        # Here, we determine which four elements of sq[] are the marks
        # To do this, we iterate through each corner of the sheet
        # On each iteration, we find the element of sq[] with the shortest distance to the corner being examined
        marks = []
        marksize = []
        h, w, c  = img.shape
        corners = [(0, 0), (0, h), (w, 0), (w,h)]
        for corner in corners:
            try:
                ind = np.argmin([(corner[0] - a[0])**2 + (corner[1] - a[1])**2 for a in sq])
            except:
                print("No markers found. Is this an empty image?")
                return -1
            marks.append(sq[ind])
            marksize.append(sqsize[ind])
            print('Corner: ' + str(corner) + "  Size:" + str(sqsize[ind]))

        #Make a copy of the list, sort the original, then calculate the median by averaging the middle 2 elements (of 4)
        u_marksize = marksize[:] #clone the list
        marksize.sort()
        median = (marksize[1] + marksize[2]) / 2

        #This block contains code to attempt to recover a sheet where the marks are not properly detected. First it will try increasing blur, then a really small blur, before finally trying to guess the location of the final mark based on the other marks
        for i,m in enumerate(u_marksize):
            if abs(1 - m/median) > 0.1: #if there is a size anomaly in markers, try some things
                print("Damaged marker detected, attempting fix: " + str(abs(1-m/median)))
                if b < 13 and b != 1 and not guess:
                    print("Increasing gaussian blur to " + str(b+2))
                    return self.loadsheet(imgpath, b=b+2)
                if b != 1 and not guess:
                    print("Trying a really small blur")
                    return self.loadsheet(imgpath, b=1)
                if not guess:
                    print("Attempting to guess the location of the last one")
                    return self.loadsheet(imgpath, b=3, guess=True)
                if i == 0: #geometry to calculate approximate position of damaged marker
                    marks[0] = (marks[1][0] - (marks[3][0]-marks[2][0]), marks[2][1] + (marks[1][1]-marks[3][1]))
                    print('Guessing top left corner')
                elif i == 1:
                    marks[1] = (marks[0][0] + (marks[3][0]-marks[2][0]), marks[3][1] + (marks[0][1]-marks[2][1]))
                    print('Guessing Bottom left corner')
                elif i == 2:
                    marks[2] = (marks[3][0] - (marks[1][0]-marks[0][0]), marks[0][1] - (marks[1][1]-marks[3][1]))
                    print('Guessing top right corner')
                elif i == 3:
                    marks[3] = (marks[2][0] + (marks[1][0]-marks[0][0]), marks[1][1] - (marks[0][1]-marks[2][1]))
                    print('Guessing bottom right corner')


        # Apply a perspective transform
        # The centers of the 4 marks become the 4 corners of the image
        pts1 = np.float32(marks)
        pts2 = np.float32([[0,0],[0,784],[560,0],[560,784]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        img = cv2.warpPerspective(img,M,(560,784))
        self.display = img.copy()
        self.sheet = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("Loading complete")
        return 1

    # Shifts all fields down by amount
    # Useful for when there are two (or more) matches on one sheet of paper
    # After reading the first match, shift down and read again
    def shiftDown (self, amount):
        self.shift = amount

    # Gets the shading value of a grid unit
    # 0 is completely shaded, 102000 is completely unshaded
    def getvalue(self, loc):
        col,row = loc
        box = self.sheet[row*16:(row+1)*16, col*16:(col+1)*16]
        return sum(map(sum, box))

    # Parses a location in Letter-Number form and returns a tuple of the pixel coordinates
    def parse(self, loc):
        col,row = loc.upper().split('-')
        return (ord(col)-67 if len(col)==1 else ord(col[1])-41, self.shift + int(row)-3)

    # Define a new boolean field at a given location
    # Returns whether or not the grid unit is shaded
    def boolfield(self, location):
        loc = self.parse(location)
        retval = int(self.getvalue(loc) < SHADED_VAL)
        if retval:
            cv2.rectangle(self.display, (loc[0]*16, loc[1]*16), (loc[0]*16+16, loc[1]*16+16), (0,50,150),3)
        return retval

    # Define a new range field at a given location
    # This field spans across multiple grid units
    # Returns the shaded value, or 0 if none is shaded
    def rangefield(self, startlocation, startval, endval):
        loc = self.parse(startlocation)
        end = loc[0]-startval+endval+1 #grid coordinate where the rangefield ends

        values = [self.getvalue((val, loc[1])) for val in range(loc[0], end)]
        min = np.asscalar(np.argmin(values))
        retval = 0
        rect = 0
        if values[min] < SHADED_VAL:
            retval = startval + min
            rect = 1
        if rect:
            cv2.rectangle(self.display, ((loc[0]+min)*16, loc[1]*16), ((loc[0]+min+1)*16, (loc[1]+1)*16), (0,50,150),3) 
        return retval

    # Define a new count field at a given location
    # This field spans across multiple grid units
    # Returns the highest shaded value, or 0 if none are shaded
    def countfield(self, startlocation, endlocation, startval):
        loc = self.parse(startlocation)
        end = self.parse(endlocation)[0] + 1

        values = [self.getvalue((val, loc[1])) for val in range(loc[0], end)]
        retval = 0
        for el,box in enumerate(values[::-1]):
            if box < SHADED_VAL:
                retval = startval + len(values) - el - 1
        if retval:
          cv2.rectangle(self.display, ((loc[0] + retval - startval)*16, loc[1]*16), ((loc[0] + retval - startval + 1)*16, loc[1]*16+16), (0,50,150),3) 
        elif (startval==0 and values[0] < SHADED_VAL):
          cv2.rectangle(self.display, ((loc[0])*16, loc[1]*16), ((loc[0] + 1)*16, loc[1]*16+16), (0,50,150),3) 
        return retval

    # Adds a data entry into the data dictionary
    def setMatchData(self, name, contents):
        self.matchData[name] = contents
    
    def setPitData(self, name, contents):
        self.pitData[name] = contents
        
    def setType(self, type):
      self.type = type

    # Opens the GUI, preparing the data for submission
    def submit(self):
        logging.debug('Inside scout.submit')
        conn = mysql.connector.connect(user=db_user, password=db_password,
                                       host=db_host,
                                       database=db_database)
        cursor = conn.cursor()
        logging.debug("Database connection complete")

        if self.type == game.SheetType.MATCH:
            logging.debug("Sheet Type is Match")
            # If the match is empty, reset the data and display fields
            if self.matchData["Team"] == 0:
                print("Found an empty match, skipping")
                logging.debug("Found an empty match, skipping")
                self.matchData = dict(game.SCOUT_FIELDS)
                self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)
                return

            query = "SELECT * FROM scout WHERE Team = %s AND `Match` = %s" % \
                    (str(self.matchData['Team']), str(self.matchData['Match']),)
            logging.debug(query)
            try:
                cursor.execute(query)
            except:
                logging.debug("Query Failed")
                raise

            history = cursor.fetchall()

            if history and not self.matchData["Replay"]:
                print("Already processed this match, skipping")
                logging.debug("Already processed this match, skipping")
                self.data = dict(game.SCOUT_FIELDS)
                self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)
                return
        elif self.type == game.SheetType.PIT:
            if self.pitData["Team"] == 0:
                print("Found an empty pit sheet, skipping")
                logging.debug("Found an empty pit sheet, skipping")
                self.pitData = dict(game.PIT_SCOUT_FIELDS)
                self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)
                return

            query = "SELECT * FROM pitScout WHERE Team = %s" % (str(self.pitData["Team"]),)
            cursor.execute(query)
            history = cursor.fetchall()

            if history:
                print("Already processed this team, skipping")
                logging.debug("Already processed this team, skipping")
                self.pitData = dict(game.PIT_SCOUT_FIELDS)
                self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)
                return

        logging.debug("Close cursor and db connection")
        cursor.close()
        conn.close()

        # Create and open the GUI to verify  data
        print("Found new data, opening")
        logging.debug("Found new data, opening")
        output = ''
        if self.type == game.SheetType.MATCH:
            for key, value in self.matchData.items():
                output += key + "=" + str(value) + '\n'

        elif self.type == game.SheetType.PIT:
            for key, value in self.pitData.items():
                output += key + "=" + str(value) + '\n'

        # TODO: Convert this to PyQt?
        fig = plt.figure('PiScout')
        fig.subplots_adjust(left=0, right=0.6)
        plt.subplot(111)
        plt.imshow(self.display)
        plt.title('Scanned Sheet')
        plt.text(600,784,output,fontsize=12)
        save = Button(plt.axes([0.68, 0.31, 0.15, 0.07]), 'Save')
        save.on_clicked(self.save)
        # upload = Button(plt.axes([0.68, 0.24, 0.15, 0.07]), 'Upload Data')
        # upload.on_clicked(self.upload)
        edit = Button(plt.axes([0.68, 0.17, 0.15, 0.07]), 'Edit Data')
        edit.on_clicked(self.edit)
        cancel = Button(plt.axes([0.68, 0.1, 0.15, 0.07]), 'Cancel')
        cancel.on_clicked(self.cancel)
        mng = plt.get_current_fig_manager()

        try:
            mng.window.state('zoomed')
        except AttributeError:
            print("Window resizing exploded, oh well.")

        plt.show()
        self.matchData = dict(game.SCOUT_FIELDS)
        self.pitData = dict(game.PIT_SCOUT_FIELDS)
        self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)

    # Invoked by the "Save Data Offline" button
    # Adds data to a queue to be uploaded online at a later time
    # Also stores in the local database
    def save(self, event):
        print("Queueing match for upload later")
        if self.type == game.SheetType.MATCH:
            with open("queue.txt", "a+") as file:
                file.write(str(self.matchData) + '\n')
            plt.close()
            requests.post("http://127.0.0.1:8000/submit",
                          data={'event': CURRENT_EVENT, 'data': str(self.matchData), 'auth': serverinfo.AUTH})
        elif self.type == game.SheetType.PIT:
            with open("pitQueue.txt", "a+") as file:
                file.write(str(self.pitData) + '\n')
            plt.close()
            requests.post("http://127.0.0.1:8000/submit",
                          data={'event': CURRENT_EVENT, 'pitData': str(self.pitData), 'auth': serverinfo.AUTH})

    # Invoked by the "Upload Data" button
    # Uploads all data (including queue) to the online database
    # Uploads a copy to the local database as backup
    def upload(self, event):
        plt.close()
        print("Attempting upload to server")

        try: #post it to piscout's ip address
            if self.type == game.SheetType.MATCH:
              requests.post(serverinfo.SERVER + "/submit", data={'event':CURRENT_EVENT, 'data': str(self.matchData), 'auth':serverinfo.AUTH})
              print("Uploading this match was successful")
              if os.path.isfile('queue.txt'):
                  with open("queue.txt", "r") as file:
                      for line in file:
                          requests.post(serverinfo.SERVER + "/submit", data={'event':CURRENT_EVENT, 'data': line, 'auth':serverinfo.AUTH})
                          print("Uploaded an entry from the queue")
                  os.remove('queue.txt')
              requests.post("http://127.0.0.1:8000/submit", data={'event':CURRENT_EVENT, 'data': str(self.matchData), 'auth':serverinfo.AUTH})
            elif self.type == game.SheetType.PIT:
              requests.post(serverinfo.SERVER + "/submit", data={'event':CURRENT_EVENT, 'pitData': str(self.pitData), 'auth':serverinfo.AUTH})
              print("Uploading this match was successful")
              if os.path.isfile('pitQueue.txt'):
                  with open("pitQueue.txt", "r") as file:
                      for line in file:
                          requests.post(serverinfo.SERVER + "/submit", data={'event':CURRENT_EVENT, 'pitData': line, 'auth':serverinfo.AUTH})
                          print("Uploaded an entry from the queue")
                  os.remove('queue.txt')
              requests.post("http://127.0.0.1:8000/submit", data={'event':CURRENT_EVENT, 'pitData': str(self.pitData), 'auth':serverinfo.AUTH})
        except:
            print("Failed miserably")
            r = self.message("Upload Failed", 'Upload failed. Retry? Otherwise, data will be stored in the queue for upload later.', type=5)
            if r == 4:
                self.upload(event)
            else:
                self.save(event)

    # Invoked by the "Edit Data" button
    # Opens up the data in notepad, and lets the user make modifications
    # Afterward, it re-opens the GUI with the updated data
    def edit(self, event):
        with open('piscout.txt', "w") as file:
          if self.type == game.SheetType.MATCH:
            file.write(json.dumps(self.matchData, indent=4))
          elif self.type == game.SheetType.PIT:
            file.write(json.dumps(self.pitData, indent=4))
        os.system('piscout.txt')
        try:
          with open('piscout.txt', 'r') as file:
            if self.type == game.SheetType.MATCH:
              self.matchData = json.load(file)
            elif self.type == game.SheetType.PIT:  
              self.pitData = json.load(file)
        except:
            self.message("Malformed Data", "You messed something up; the data couldn't be read. Try again.")
        plt.close()
        self.submit()

    # Invoked by the "Cancel" button
    # Closes the GUI and erases the entry from the history file
    def cancel(self, event):
        plt.close()

    # Displays a message box
    def message(self, title, message, type=0):
        return ctypes.windll.user32.MessageBoxW(0, message, title, type)

PiScout()