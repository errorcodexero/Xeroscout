import numpy as np
import sqlite3 as sql
from enum import IntEnum
import proprietary as prop

# Defines the fields stored in the "Scout" table of the database. This database
# stores the record for each match scan
SCOUT_FIELDS = {"Team": 0, "Match": 0, "Replay": 0,
                "Autoline": 0, "StartPositionFarLeft": 0,
                "StartPositionLeft": 0, "StartPositionCenter": 0,
                "StartPositionRight": 0,
                "AutoBallsLow": 0, "AutoBallsHigh": 0,
                "TeleBallsLow": 0, "TeleBallsHigh": 0,
                "BallTrenchRange": 0, "ControlPanelRotation": 0,
                "ControlPanelPosition": 0,
                "EndgameParks": 0, "EndgameAssisted": 0, 
                "EndgameClimbCenter": 0, "EndgameClimbSide": 0,
                "EndgameAssists": 0,
                "Breakdown": 0, "Brownout": 0,
                "FlexField": 0,
                }

# Defines the fields that are stored in the "averages" and similar tables of the database.
# These are the fields displayed on the home page of the website. Hidden average fields
# are only displayed when logged in or on local.
AVERAGE_FIELDS = {"team": 0, "apr": 0, "AutoCrates": 0, }
HIDDEN_AVERAGE_FIELDS = {"CubeScore": 0, "FirstP": 0, "SecondP": 0, }

# Define the fields collected from Pit Scouting to display on the team page
PIT_SCOUT_FIELDS = {"Team": 0, "Weight": 0, "Language": '', "Drivebase": '',
                    "Wheels": 0, "Cims": 0, "Neos": 0, "Falcons": 0,
                    "PosStartPositionFarLeft": 0, "PosStartPositionLeft": 0,
                    "PosStartPositionCenter": 0,
                    "PosStartPositionRight": 0,
                    "PrefStartPositionLeft": 0, "PrefStartPositionFarLeft": 0,
                    "PrefStartPositionCenter": 0,
                    "PrefStartPositionRight": 0,
                    "MaxAutoBallsLow": 0, "MaxAutoBallsHigh": 0,
                    "TraversesControlPanel": 0,
                    "ControlPanelRotation": 0, "ControlPanelPosition": 0, 
                    "GroundCollection": 0, "BallTrenchRange": 0,
                    "TeleBallsLow": 0, "TeleBallsHigh": 0,
                    "EndgameClimbCenter": 0, "EndgameClimbSide": 0,
                    "EndgameClimbTiltLow": 0, "EndgameClimbTiltMiddle": 0,
                    "EndgameClimbTiltHigh": 0,
                    "EndgameLevelMechanism": 0, "EndgameAssists": 0, 
                    }

# Defines the fields displayed on the charts on the team and compare pages
CHART_FIELDS = {"match": 0, "TeleBunniesPlaced": 0, }


class SheetType(IntEnum):
    MATCH = 0
    PIT = 1
        
     
# Main method to process a full-page sheet
# Submits three times, because there are three matches on one sheet
# The sheet is developed in Google Sheets and the coordinates are defined in
# terms on the row and column numbers from the sheet.
def processSheet(scout):
    for s in (0, 16, 32):
        # Sets the shift value (used when turning cell coordinates into pixel coordinates)
        scout.shiftDown(s)
        
        type = scout.rangefield('E-5', 0, 1)
        scout.setType(type)
        if type == SheetType.MATCH:
            # Match scouting sheet
            # Team Number
            num1 = scout.rangefield('D-14', 0, 9)
            num2 = scout.rangefield('D-15', 0, 9)
            num3 = scout.rangefield('D-16', 0, 9)
            num4 = scout.rangefield('D-17', 0, 9)
           
            '''
            if scout.boolfield('K-13') == 1:
                teamletter = 'A'
            elif scout.boolfield('L-13') == 1:
                teamletter = 'B'
            elif scout.boolfield('M-13') == 1:
                teamletter = 'C'
            else:
                teamletter = ''
            '''
            
            scout.setMatchData("Team", str(1000*num1 + 100*num2 + 10*num3 + num4))


            # Match Number
            
            match1 = scout.rangefield('D-9', 0, 1)
            match2 = scout.rangefield('D-10', 0, 9)
            match3 = scout.rangefield('D-11', 0, 9)
            scout.setMatchData("Match", str(100*match1 + 10*match2 + match3))

            scout.setMatchData("Replay", scout.boolfield('M-9'))

            # Auto
            scout.setMatchData("Autoline", scout.boolfield("S-6"))
            scout.setMatchData("AutoBallsLow", scout.rangefield("Q-8", 1, 10))
            scout.setMatchData("AutoBallsHigh", scout.rangefield("Q-9", 1, 10))
            scout.setMatchData("StartPositionFarLeft", scout.boolfield("V-6"))
            scout.setMatchData("StartPositionLeft", scout.boolfield("W-6"))
            scout.setMatchData("StartPositionCenter", scout.boolfield("X-6"))
            scout.setMatchData("StartPositionRight", scout.boolfield("Y-6"))

            # Teleop
            scout.setMatchData("Breakdown", scout.boolfield('AK-16'))
            scout.setMatchData("Brownout", scout.boolfield('AK-17'))

            lowball1 = scout.rangefield('P-13', 0, 9)
            lowball2 = scout.rangefield('P-14', 0, 9)
          
            scout.setMatchData("TeleBallsHigh", str(10*lowball1 + lowball2))
            
            highball1 = scout.rangefield('P-16', 0, 9)
            highball2 = scout.rangefield('P-17', 0, 9)
          
            scout.setMatchData("TeleBallsHigh", str(10*highball1 + highball2))
            
            scout.setMatchData("BallTrenchRange", scout.boolfield('AK-14'))
            
            scout.setMatchData("ControlPanelRotation", scout.boolfield('AF-16'))
            scout.setMatchData("ControlPanelPosition", scout.boolfield('AF-17'))
            
            #Endgame
            
            scout.setMatchData("EndgameParks", scout.boolfield('AF-6'))
            scout.setMatchData("EndgameAssisted", scout.boolfield('AJ-6'))
            scout.setMatchData("EndgameClimbCenter", scout.boolfield('A1-7'))
            scout.setMatchData("EndgameClimbSide", scout.boolfield('A1-8'))
            
            scout.setMatchData("EndgameAssists", scout.rangefield("A1-9", 1, 2))
            
            
            #Defense
            
            scout.submit()

        elif type == SheetType.PIT:
            # Pit scouting sheet
            # Team Number
            num1 = scout.rangefield('E-8', 0, 9)
            num2 = scout.rangefield('E-9', 0, 9)
            num3 = scout.rangefield('E-10', 0, 9)
            num4 = scout.rangefield('E-11', 0, 9)
            
            '''
            if scout.boolfield('L-7') == 1:
                teamletter = 'A'
            elif scout.boolfield('M-7') == 1:
                teamletter = 'B'
            elif scout.boolfield('N-7') == 1:
                teamletter = 'C'
            else:
                teamletter = ''
            '''
            
            scout.setPitData("Team", str(1000*num1 + 100*num2 + 10*num3 + num4))

            # Weight
            weight1 = scout.rangefield('E-15', 0, 1)
            weight2 = scout.rangefield('E-16', 0, 9)
            weight3 = scout.rangefield('E-17', 0, 9)
            scout.setPitData("Weight", 100*weight1 + 10*weight2 + weight3)

            # Drive base
            drive_type = ''
            if scout.boolfield('U-6') == 1:
                drive_type = 'Mecanum'
            elif scout.boolfield('U-7') == 1:
                drive_type = 'West Coast'
            elif scout.boolfield('X-6') == 1:
                drive_type = 'Swerve'
            elif scout.boolfield('X-7') == 1:
                drive_type = 'Other'
            else:
                'Other'
            scout.setPitData("Drivebase", drive_type)

            # Programming Language
            prog_lang = ''
            if scout.boolfield('K-14') == 1:
                prog_lang = 'CPP'
            elif scout.boolfield('L-14'):
                prog_lang = 'Java'
            elif scout.boolfield('M-14'):
                prog_lang = 'LabVIEW'
            elif scout.boolfield('N-14'):
                prog_lang = 'Other'
            else:
                'Other'
            scout.setPitData("Language", prog_lang)

            scout.setPitData("Wheels", scout.rangefield('T-9', 3, 6))
            scout.setPitData("Cims", scout.rangefield('T-10', 2, 6))
            scout.setPitData("Neos", scout.rangefield('T-11', 1, 4))
            scout.setPitData("Falcons", scout.rangefield('T-12', 1, 4))
            
            scout.setPitData("PosStartPositionFarLeft", scout.boolfield('AE-6'))
            scout.setPitData("PosStartPositionLeft", scout.boolfield('AF-6'))
            scout.setPitData("PosStartPositionCenter", scout.boolfield('AG-6'))
            scout.setPitData("PosStartPositionRight", scout.boolfield('AH-6'))
            scout.setPitData("PrefStartPositionFarLeft", scout.boolfield('AE-7'))
            scout.setPitData("PrefStartPositionLeft", scout.boolfield('AF-7'))
            scout.setPitData("PrefStartPositionCenter", scout.boolfield('AG-7'))
            scout.setPitData("PrefStartPositionRight", scout.boolfield('AH-7'))
            
            scout.setPitData("MaxAutoBallsLow", scout.rangefield('AC-10', 1, 9))
            scout.setPitData("MaxAutoBallsHigh", scout.rangefield('AC-11', 1, 9))
            
            scout.setPitData("TraversesControlPanel", scout.boolfield('V-15'))
            scout.setPitData("ControlPanelRotation", scout.boolfield('V-16'))
            scout.setPitData("ControlPanelPosition", scout.boolfield('V-17'))
            scout.setPitData("GroundCollection", scout.boolfield('AD-14'))
            scout.setPitData("TeleBallsLow", scout.boolfield('AD-15'))
            scout.setPitData("TeleBallsHigh", scout.boolfield('AD-16'))
            scout.setPitData("BallTrenchRange", scout.boolfield('AD-17'))
            
            scout.setPitData("EndgameClimbCenter", scout.boolfield('AK-13'))
            scout.setPitData("EndgameClimbSide", scout.boolfield('AK-14'))
            scout.setPitData("EndgameClimbTiltLow", scout.boolfield('AK-15'))
            scout.setPitData("EndgameClimbTiltMiddle", scout.boolfield('AJ-15'))
            scout.setPitData("EndgameClimbTiltHigh", scout.boolfield('AI-15'))
            scout.setPitData("EndgameLevelMechanism", scout.boolfield('AK-16'))
            scout.setPitData("EndgameAssists", scout.rangefield('AJ-17', 1, 2))
            
            
            scout.submit()


# Takes an entry from the Scout database table and generates text for display on the team page. This page
# has 4 columns, currently used for auto, 2 teleop, and other (like fouls and end game)
def generateTeamText(e):
    text = {'auto': "", 'teleop1': "", 'teleop2': "", 'other': ""}
    text['auto'] += 'Start: '
    text['auto'] += 'L' if e['Start'] == 0 else 'C' if e['Start'] == 1 else 'R'

    text['teleop1'] += 'DUMMY'

    text['teleop2'] += 'DUMMY'

    text['other'] = 'DUMMY'

    return text


# Takes an entry from the Scout database table and generates chart data. The fields in the returned
# dict must match the CHART_FIELDS definition at the top of this file
def generateChartData(e):
    dp = dict(CHART_FIELDS)
    dp["match"]= e['match']
    
    dp['TeleBunniesPlaced'] += e['TeleBunniesPlaced']

    return dp


# Takes a set of team numbers and a string indicating quals or playoffs and returns a prediction
# for the alliances score and whether or not they will achieve any additional ranking points
def predictScore(datapath, teams, level='quals'):
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        
        autoRP = 0
        climbRP = 0
        climbTotal = 0
        
        aprTotal = 0

        for n in teams:
            average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
              entry = average[0]
            else:
              entry = dict(AVERAGE_FIELDS)
              entry.update(HIDDEN_AVERAGE_FIELDS)
            
            aprTotal += entry['CubeScore']
              
        retVal = {'score': 0, 'RP1': 0, 'RP2': 0}
       
        retVal['score'] = aprTotal
        
        return retVal


# Takes an entry from the Scout table and returns whether or not the entry should be flagged based on contradictory data.
def autoFlag(entry):
    return 0


# Takes a list of Scout table entries and returns a nested dictionary of the statistical calculations (average, maxes, median, etc.) of each field in the AVERAGE_FIELDS definition
def calcTotals(entries):
    sums = dict(AVERAGE_FIELDS)
    sums.update(HIDDEN_AVERAGE_FIELDS)
    noDefense = dict(AVERAGE_FIELDS)
    noDefense.update(HIDDEN_AVERAGE_FIELDS)
    lastThree = dict(AVERAGE_FIELDS)
    lastThree.update(HIDDEN_AVERAGE_FIELDS)
    noDCount = 0
    lastThreeCount = 0
    for key in sums:
        sums[key] = []
    # For each entry, add components to the running total if appropriate
    for i, e in enumerate(entries):
        pass
    
    # If there is data, average out the last 3 or less matches
    if(lastThreeCount):
        for key,val in lastThree.items():
            lastThree[key] = round(val/lastThreeCount, 2)
          
    # If there were matches where the team didn't play D, average those out
    if noDCount:
        for key,val in noDefense.items():
            noDefense[key] = round(val/noDCount, 2)
            
    average = dict(AVERAGE_FIELDS)
    median = dict(AVERAGE_FIELDS)
    maxes = dict(AVERAGE_FIELDS)
    for key in sums:
        if key != 'team' and key!= 'apr':
            average[key] = round(np.mean(sums[key]), 2)
            median[key] = round(np.median(sums[key]), 2)
            maxes[key] = round(np.max(sums[key]), 2)
    retVal = {'averages':average, 'median':median, 'maxes':maxes, 'noDefense':noDefense, 'lastThree':lastThree}
    
    # Calculate APRs. This is an approximate average points contribution to the match
    for key in retVal:
        CubeScore = 1
        FirstPick = 1
        SecondPick = 1
        apr = 1
        
        retVal[key]['CubeScore'] = CubeScore
        retVal[key]['FirstP'] = FirstPick
        retVal[key]['SecondP'] = SecondPick
        retVal[key]['apr'] = apr
    
    return retVal
            
        