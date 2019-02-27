import numpy as np
import sqlite3 as sql
from enum import IntEnum
import proprietary as prop

# Defines the fields stored in the "Scout" table of the database. This database
# stores the record for each match scan
SCOUT_FIELDS = {"Team": 0, "Match": 0, "Replay": 0,
                "StartPosL": 0, "StartPosC": 0, "StartPosR": 0,
                "StartLvl": 0, "HatchPreload": 0, "CargoPreload": 0,
                "SandCross": 0, "SandHatches": 0, "SandCargo": 0,
                "SandAuto": 0, "SandVision": 0,
                "TeleBreakdown": 0, "TeleBrownout": 0, "TeleDefense": 0,
                "HatchShipL1": 0, "HatchShipL2": 0, "HatchShipL3": 0, "HatchShipLF": 0,
                "HatchShipR1": 0, "HatchShipR2": 0, "HatchShipR3": 0, "HatchShipRF": 0,
                "CargoShipL1": 0, "CargoShipL2": 0, "CargoShipL3": 0, "CargoShipLF": 0,
                "CargoShipR1": 0, "CargoShipR2": 0, "CargoShipR3": 0, "CargoShipRF": 0,
                "ShipHatchTotal": 0, "ShipCargoTotal": 0,
                "RocketHatchLL1": 0, "RocketHatchLL2": 0, "RocketHatchLL3": 0,
                "RocketHatchLR1": 0, "RocketHatchLR2": 0, "RocketHatchLR3": 0,
                "RocketHatchRL1": 0, "RocketHatchRL2": 0, "RocketHatchRL3": 0,
                "RocketHatchRR1": 0, "RocketHatchRR2": 0, "RocketHatchRR3": 0,
                "RocketCargoLL1": 0, "RocketCargoLL2": 0, "RocketCargoLL3": 0,
                "RocketCargoLR1": 0, "RocketCargoLR2": 0, "RocketCargoLR3": 0,
                "RocketCargoRL1": 0, "RocketCargoRL2": 0, "RocketCargoRL3": 0,
                "RocketCargoRR1": 0, "RocketCargoRR2": 0, "RocketCargoRR3": 0,
                "RocketHatchTotal": 0, "RocketCargoTotal": 0,
                "ClimbSelf": 0, "AssistOther1": 0, "AssistOther2": 0,
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
            num1 = scout.rangefield('AB-5', 0, 9)
            num2 = scout.rangefield('AB-6', 0, 9)
            num3 = scout.rangefield('AB-7', 0, 9)
            num4 = scout.rangefield('AB-8', 0, 9)

            scout.setMatchData("Team", str(1000*num1 + 100*num2 + 10*num3 + num4))

            match1 = scout.rangefield('J-5', 0, 1)
            match2 = scout.rangefield('J-6', 0, 9)
            match3 = scout.rangefield('J-7', 0, 9)
            scout.setMatchData("Match", str(100*match1 + 10*match2 + match3))

            scout.setMatchData("Replay", scout.boolfield('S-5'))

            # Sandstorm
            scout.setMatchData("StartPosL", scout.boolfield("F-11"))
            scout.setMatchData("StartPosC", scout.boolfield("G-11"))
            scout.setMatchData("StartPosR", scout.boolfield("H-11"))
            scout.setMatchData("StartLvl", scout.rangefield('F-12', 1, 2))
            scout.setMatchData("SandCross", scout.boolfield('F-13'))

            scout.setMatchData("SandHatches", scout.countfield('F-15', 'M-15', 0))
            scout.setMatchData("SandCargo", scout.countfield('F-16', 'M-16', 0))

            scout.setMatchData("SandAuto", scout.boolfield('M-10'))
            scout.setMatchData("SandVision", scout.boolfield('N-10'))

            sand_hatch_1 = scout.boolfield('J-13')
            sand_hatch_2 = scout.boolfield('N-13')

            scout.setMatchData("HatchPreload", sand_hatch_1+sand_hatch_2)
            scout.setMatchData("CargoPreload", 2-sand_hatch_1+sand_hatch_2)

            # Teleop
            scout.setMatchData("TeleDefense", scout.boolfield('AK-15'))
            scout.setMatchData("TeleBreakdown", scout.boolfield('AK-16'))
            scout.setMatchData("TeleBrownout", scout.boolfield('AK-17'))

            scout.setMatchData("ClimbSelf", scout.rangefield('AI-11', 1, 3))
            scout.setMatchData("AssistOther1", scout.rangefield('AJ-12', 2, 3))
            scout.setMatchData("AssistOther2", scout.rangefield('AJ-13', 2, 3))

            scout.setMatchData("CargoShipL1", scout.boolfield('W-10'))
            scout.setMatchData("CargoShipL2", scout.boolfield('W-11'))
            scout.setMatchData("CargoShipL3", scout.boolfield('W-12'))
            scout.setMatchData("CargoShipR1", scout.boolfield('X-10'))
            scout.setMatchData("CargoShipR2", scout.boolfield('X-11'))
            scout.setMatchData("CargoShipR3", scout.boolfield('X-12'))
            scout.setMatchData("CargoShipLF", scout.boolfield('W-13'))
            scout.setMatchData("CargoShipRF", scout.boolfield('X-13'))
            
            scout.setMatchData("ShipCargoTotal", 
                               scout.boolfield('W-10') +
                               scout.boolfield('W-11') +
                               scout.boolfield('W-12') +
                               scout.boolfield('X-10') +
                               scout.boolfield('X-11') +
                               scout.boolfield('x-12') +
                               scout.boolfield('W-13') +
                               scout.boolfield('X-13'))
            
            scout.setMatchData("HatchShipL1", scout.boolfield('V-10'))
            scout.setMatchData("HatchShipL2", scout.boolfield('V-11'))
            scout.setMatchData("HatchShipL3", scout.boolfield('V-12'))
            scout.setMatchData("HatchShipR1", scout.boolfield('Y-10'))
            scout.setMatchData("HatchShipR2", scout.boolfield('Y-12'))
            scout.setMatchData("HatchShipR3", scout.boolfield('Y-13'))
            scout.setMatchData("HatchShipLF", scout.boolfield('W-14'))
            scout.setMatchData("HatchShipRF", scout.boolfield('X-14'))
            
            scout.setMatchData("ShipHatchTotal", 
                               scout.boolfield('V-10') +
                               scout.boolfield('V-11') +
                               scout.boolfield('V-12') +
                               scout.boolfield('Y-10') +
                               scout.boolfield('Y-11') +
                               scout.boolfield('Y-12') +
                               scout.boolfield('W-14') +
                               scout.boolfield('X-14'))

            scout.setMatchData("RocketHatchLL1", scout.boolfield('R-17'))
            scout.setMatchData("RocketHatchLL2", scout.boolfield('R-16'))
            scout.setMatchData("RocketHatchLL3", scout.boolfield('R-15'))
            scout.setMatchData("RocketHatchLR1", scout.boolfield('U-17'))
            scout.setMatchData("RocketHatchLR2", scout.boolfield('U-16'))
            scout.setMatchData("RocketHatchLR3", scout.boolfield('U-15'))

            scout.setMatchData("RocketHatchRL1", scout.boolfield('Z-17'))
            scout.setMatchData("RocketHatchRL2", scout.boolfield('Z-16'))
            scout.setMatchData("RocketHatchRL3", scout.boolfield('Z-15'))
            scout.setMatchData("RocketHatchRR1", scout.boolfield('AC-17'))
            scout.setMatchData("RocketHatchRR2", scout.boolfield('AC-16'))
            scout.setMatchData("RocketHatchRR3", scout.boolfield('AC-15'))
            
            scout.setMatchData("RocketHatchTotal", 
                               scout.boolfield('R-17') +
                               scout.boolfield('R-16') +
                               scout.boolfield('R-15') +
                               scout.boolfield('U-17') +
                               scout.boolfield('U-16') +
                               scout.boolfield('U-15') +
                               scout.boolfield('Z-17') +
                               scout.boolfield('Z-16') +
                               scout.boolfield('Z-15') +
                               scout.boolfield('AC-17') +
                               scout.boolfield('AC-16') +
                               scout.boolfield('AC-15'))

            scout.setMatchData("RocketCargoLL1", scout.boolfield('S-17'))
            scout.setMatchData("RocketCargoLL2", scout.boolfield('S-16'))
            scout.setMatchData("RocketCargoLL3", scout.boolfield('S-15'))
            scout.setMatchData("RocketCargoLR1", scout.boolfield('T-17'))
            scout.setMatchData("RocketCargoLR2", scout.boolfield('T-16'))
            scout.setMatchData("RocketCargoLR3", scout.boolfield('T-15'))

            scout.setMatchData("RocketCargoRL1", scout.boolfield('AA-17'))
            scout.setMatchData("RocketCargoRL2", scout.boolfield('AA-16'))
            scout.setMatchData("RocketCargoRL3", scout.boolfield('AA-15'))
            scout.setMatchData("RocketCargoRR1", scout.boolfield('AB-17'))
            scout.setMatchData("RocketCargoRR2", scout.boolfield('AB-16'))
            scout.setMatchData("RocketCargoRR3", scout.boolfield('AB-15'))
            
            scout.setMatchData("RocketCargoTotal", 
                               scout.boolfield('S-17') +
                               scout.boolfield('S-16') +
                               scout.boolfield('S-15') +
                               scout.boolfield('T-17') +
                               scout.boolfield('T-16') +
                               scout.boolfield('T-15') +
                               scout.boolfield('AA-17') +
                               scout.boolfield('AA-16') +
                               scout.boolfield('AA-15') +
                               scout.boolfield('AB-17') +
                               scout.boolfield('AB-16') +
                               scout.boolfield('AB-15'))

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


# Takes an entry from the Scout database table and generates text for display on the team page. This page has 4 columns, currently used for auto, 2 teleop, and other (like fouls and end game)
def generateTeamText(e):
    text = {'auto': "", 'teleop1': "", 'teleop2': "", 'other': ""}
    text['auto'] += 'Start: '
    text['auto'] += 'L' if e['Start'] == 0 else 'C' if e['Start'] == 1 else 'R'

    text['teleop1'] += 'DUMMY'

    text['teleop2'] += 'DUMMY'

    text['other'] = 'DUMMY'

    return text


# Takes an entry from the Scout database table and generates chart data. The fields in the returned dict must match the CHART_FIELDS definition at the top of this file
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
            
        