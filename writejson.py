import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f","--fileLocation", help="path to the monLogger file")
args = parser.parse_args()

f = open(args.fileLocation,"r")

f.seek(0)
header = f.readline()
configDict = {}
colToShow = []
for colname in header.split():
    colToShow.append(colname)
configDict["columnToShow"] = colToShow
print (json.dumps(configDict,indent=4))
