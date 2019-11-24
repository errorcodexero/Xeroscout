import numpy as np
import sqlite3 as sql
from enum import IntEnum
import proprietary as prop

# Defines the fields stored in the "Scout" table of the database. This database
# stores the record for each match scan
SCOUT_FIELDS = {"Team": '', "Match": 0, "Replay": 0,
                "AutoBunniesCollected": 0, "AutoTubsTouched": 0,
                "AutoTubLifted": 0, "AutoDefensive": 0,
                "TeleBunniesPlaced": 0, "TeleBunniesEjected": 0, 
                "TeleGroundCubeCollection": 0, "TeleBreakdown": 0,
                "TeleBrownout": 0, "TotalCubesCollected": 0,
                "TeleTotalKnockedCubes": 0, "FinalTotalCubesCollected": 0,
                "FlexField": 0,
                }

# Defines the fields that are stored in the "averages" and similar tables of the database.
# These are the fields displayed on the home page of the website. Hidden average fields
# are only displayed when logged in or on local.
AVERAGE_FIELDS = {"team": 0, "apr": 0, "AutoCrates": 0, }
HIDDEN_AVERAGE_FIELDS = {"CubeScore": 0, "FirstP": 0, "SecondP": 0, }

# Define the fields collected from Pit Scouting to display on the team page
PIT_SCOUT_FIELDS = {"Team": 0, "Weight": 0, "Language": '', "Drivebase": '',
                    "Wheels": 0, "Sims": 0, "Neos": 0,
                    "StartLevel": 0, "Vision": 0, "Autonomous": 0,
                    "LoadHatch": 0, "PickUpHatch": 0, "CargoShipHatch": 0,
                    "RocketL1Hatch": 0, "RocketL2Hatch": 0, "RocketL3Hatch": 0,
                    "LoadCargo": 0, "PickUpCargo": 0, "CargoShipCargo": 0,
                    "RocketL1Cargo": 0, "RocketL2Cargo": 0, "RocketL3Cargo": 0,
                    "ClimbLevel": 0, "CoopClimb": 0,
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
            
            if scout.boolfield('K-13') == 1:
                teamletter = 'A'
            elif scout.boolfield('L-13') == 1:
                teamletter = 'B'
            elif scout.boolfield('M-13') == 1:
                teamletter = 'C'
            else:
                teamletter = ''

            scout.setMatchData("Team", str(1000*num1 + 100*num2 + 10*num3 + num4) + teamletter)

            # Match Number
            match1 = scout.rangefield('D-9', 0, 1)
            match2 = scout.rangefield('D-10', 0, 9)
            match3 = scout.rangefield('D-11', 0, 9)
            scout.setMatchData("Match", str(100*match1 + 10*match2 + match3))

            scout.setMatchData("Replay", scout.boolfield('M-9'))

            # Auto
            scout.setMatchData("AutoBunniesCollected", scout.rangefield("V-6", 0, 2))
            scout.setMatchData("AutoTubsTouched", scout.rangefield("V-7", 0, 2))
            scout.setMatchData("AutoTubLifted", scout.boolfield("V-8"))
            scout.setMatchData("AutoDefensive", scout.boolfield("V-9"))


            # Teleop
            scout.setMatchData("TeleBreakdown", scout.boolfield('AJ-9'))
            scout.setMatchData("TeleBrownout", scout.boolfield('AJ-10'))

            #Defense
            

            scout.setMatchData("TeleBunniesPlaced", scout.countfield('AH-5', 'AJ-5', 1))
            scout.setMatchData("TeleBunniesEjected", scout.countfield('AH-6', 'AJ-6', 1))
            scout.setMatchData("TeleGroundCubeCollection", scout.boolfield('AJ-8'))
            
            Total_Cubes = scout.rangefield('O-13', 0, 13)
            if Total_Cubes < 6:
                scout.setMatchData("TotalCubesCollected", Total_Cubes)
            elif Total_Cubes < 11:
                scout.setMatchData("TotalCubesCollected", (Total_Cubes - 4) * 5)
            elif Total_Cubes < 15:
                scout.setMatchData("TotalCubesCollected", (Total_Cubes - 7) * 10)
            
            Total_Knocked_Cubes = scout.rangefield('O-15', 0, 13)
            if Total_Knocked_Cubes < 6:
                scout.setMatchData("TeleTotalKnockedCubes", Total_Knocked_Cubes)
            elif Total_Knocked_Cubes < 11:
                scout.setMatchData("TeleTotalKnockedCubes", (Total_Knocked_Cubes - 4) * 5)
            elif Total_Knocked_Cubes < 15:
                scout.setMatchData("TeleTotalKnockedCubes", (Total_Knocked_Cubes - 7) * 10)
                
            Final_Total_Cubes = scout.rangefield('O-17', 0, 13)
            if Final_Total_Cubes < 6:
                scout.setMatchData("FinalTotalCubesCollected", Final_Total_Cubes)
            elif Final_Total_Cubes < 11:
                scout.setMatchData("FinalTotalCubesCollected", (Final_Total_Cubes - 4) * 5)
            elif Final_Total_Cubes < 15:
                scout.setMatchData("FinalTotalCubesCollected", (Final_Total_Cubes - 7) * 10)

            scout.submit()
        elif type == SheetType.PIT:
            # Pit scouting sheet
            # Team Number
            num1 = scout.rangefield('M-5', 0, 9)
            num2 = scout.rangefield('M-6', 0, 9)
            num3 = scout.rangefield('M-7', 0, 9)
            num4 = scout.rangefield('M-8', 0, 9)
            scout.setPitData("Team", 1000*num1 + 100*num2 + 10*num3 + num4)

            # Weight
            weight1 = scout.rangefield('AB-5', 0, 1)
            weight2 = scout.rangefield('AB-6', 0, 9)
            weight3 = scout.rangefield('AB-7', 0, 9)
            scout.setPitData("Weight", 100*weight1 + 10*weight2 + weight3)

            # Drive base
            drive_type = ''
            if scout.boolfield('E-11') == 1:
                drive_type = 'Mecanum'
            elif scout.boolfield('E-12') == 1:
                drive_type = 'West Coast'
            elif scout.boolfield('I-11') == 1:
                drive_type = 'Swerve'
            elif scout.boolfield('I-12') == 1:
                drive_type = 'Other'
            else:
                'Other'
            scout.setPitData("Drivebase", drive_type)

            # Programming Language
            prog_lang = ''
            if scout.boolfield('W-10') == 1:
                prog_lang = 'CPP'
            elif scout.boolfield('X-10'):
                prog_lang = 'Java'
            elif scout.boolfield('Y-10'):
                prog_lang = 'LabVIEW'
            elif scout.boolfield('Z-10'):
                prog_lang = 'Other'
            else:
                'Other'
            scout.setPitData("Language", prog_lang)

            scout.setPitData("Wheels", scout.rangefield('E-14', 3, 6))
            scout.setPitData("Sims", scout.rangefield('E-15', 2, 6))
            scout.setPitData("Neos", scout.rangefield('E-16', 1, 4))

            # Manipulator
            scout.setPitData("LoadHatch", scout.boolfield('Q-11'))
            scout.setPitData("PickUpHatch", scout.boolfield('Q-12'))
            scout.setPitData("CargoShipHatch", scout.boolfield('Q-13'))
            scout.setPitData("RocketL1Hatch", scout.boolfield('Q-14'))
            scout.setPitData("RocketL2Hatch", scout.boolfield('Q-15'))
            scout.setPitData("RocketL3Hatch", scout.boolfield('Q-16'))

            scout.setPitData("LoadCargo", scout.boolfield('R-11'))
            scout.setPitData("PickUpCargo", scout.boolfield('R-12'))
            scout.setPitData("CargoShipCargo", scout.boolfield('R-13'))
            scout.setPitData("RocketL1Cargo", scout.boolfield('R-14'))
            scout.setPitData("RocketL2Cargo", scout.boolfield('R-15'))
            scout.setPitData("RocketL3Cargo", scout.boolfield('R-16'))

            # Auto
            scout.setPitData("StartLevel", scout.rangefield('X-12', 1, 2))
            scout.setPitData("Vision", scout.boolfield('X-13'))
            scout.setPitData("Autonomous", scout.boolfield('X-14'))

            # Endgame
            scout.setPitData("ClimbLevel", scout.rangefield('X-16', 1, 3))
            scout.setPitData("CoopClimb", scout.boolfield('X-17'))

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
            
        