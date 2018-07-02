import os.path
import argparse
import linecache
import json
import sys
from datetime import datetime
from prettytable import PrettyTable
from ROOT import *

def makeAllplots(graphs,cvf,title):
    gROOT.SetBatch()
    mg     = TMultiGraph()
    nGraphs= 0
    can = TCanvas("c","c",800,600)
    if "multiGraph" in title:
        can.SetLogy(1)
    leg = TLegend(0.7,0.7,0.9,0.9)
    for gName,g in graphs.iteritems():
        if g.GetN()==0:continue
        mg.Add(g)
        g.SetLineColor(nGraphs+1)
        g.SetFillColor(nGraphs+1)
        g.SetMarkerStyle(kFullCircle)
        g.SetMarkerSize(0.5)
        leg.AddEntry(g,gName,"lp")
        nGraphs +=1
    filterInfo=""
    for Filter in cvf:
        filterInfo += "%s %s %s "%(Filter['colname'],Filter['logic'],Filter['value'])
    mg.SetTitle(filterInfo)
    mg.Draw("alp")
    mg.GetXaxis().SetTimeDisplay(1)
    leg.Draw("same")
    can.SaveAs('%s.pdf'%title)

        

#return int value of time to be filled in ROOT
def convertTimeString(timeString):
    ts = datetime.strptime(timeString,'%Y-%m-%dT%H:%M:%S.%f')
    t  = TDatime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
    return t.Convert()
    
def printRequest(fileLocation,startTime,maxLine,columnValueFilter,EndTime=None):
    filterInfo = ""
    if columnValueFilter is not []:
        for Filter in columnValueFilter:
            filterInfo += "%s %s %s \n "%(Filter['colname'],Filter['logic'],Filter['value'])
    if EndTime is not None:
        infoLine = "Printing file= {0} ,  startTime = {1},  EndTime={2},  maxLine = {3}".format(fileLocation,startTime,EndTime,maxLine)
    else:
        infoLine = "Printing file= {0} ,  startTime = {1},  maxLine = {2}".format(fileLocation,startTime,maxLine)

    print "==============================================================================================================================================" 
    print infoLine
    print "==============================================================================================================================================" 
    if filterInfo is not "":
        print "Applying the following filters:"
        print filterInfo
def seekStartTime(f,startTime):
    print "Seeking startTime = ", startTime
    NextSeekline,seekline  = 2,2
    timestamp = datetime(2000,1,1)
    line          = linecache.getline(f,NextSeekline).strip().split()
    while len(line)>0 and timestamp < startTime:
        sys.stdout.write('.')
        sys.stdout.flush()
        seekline      = NextSeekline
        NextSeekline +=50000
        line          = linecache.getline(f,NextSeekline).strip().split()
        if len(line)>0:
            timeString   = line[0].replace("+02:00","").replace("+01:00","")
            timestamp   = datetime.strptime(timeString,'%Y-%m-%dT%H:%M:%S.%f')
    print "Skipping to line =%s, be patience "%seekline 
    return seekline
     
def loadfile(f,startTime,maxLine,EndTime=None):
    if os.path.exists(f):
        loggerTable = []
        logfile = open(f)
        logfile.seek(0)
        header      = logfile.readline().split()
        nLine       = seekStartTime(f,startTime)
        logfile.seek(0)
        for i in range(0,nLine):
            next(logfile)
        for line in logfile:
            line = line.strip().replace('"',"").split()
            timeString   = line[0].replace("+02:00","").replace("+01:00","")
            timestamp   = datetime.strptime(timeString,'%Y-%m-%dT%H:%M:%S.%f')
            thisSecond  = timestamp.second
            if (startTime is not None):
                if( timestamp > startTime and len(loggerTable)<maxLine):
                    if(EndTime is None or timestamp < EndTime):
                        row = {}
                        # Header row is row[colname] = value
                        for icol in range(0,len(header)):
                            row[header[icol]] = line[icol]
                        loggerTable.append(row)
                else:
                    continue
            else:
                print "You must provide a starttime"
        return loggerTable
    else:
        print "file %s does not exists. Are you on hcalmon?"%f
        
###########################################
parser = argparse.ArgumentParser()
parser.add_argument("--fileLocation", help="path to the monLogger file")
parser.add_argument("--maxLine"     , help="number of OutputLine from StartTime", type=int, default=10)
parser.add_argument("--printConfig" , help="json file to filter output")
parser.add_argument("--startTime"   , help="StartTime to look for lines, format: yyyy-mm-dd HH:MM", required=True)
parser.add_argument("--endTime"     , help="EndTime   to look for lines, format: yyyy-mm-dd HH:MM")
args = parser.parse_args()

fileLocation = args.fileLocation
maxLine      = args.maxLine
columnToShow     =[]
columnValueFilter=[]
if(args.printConfig is not None):
    printConfigFile=open(args.printConfig)
    printConfig       = json.load(printConfigFile)
    columnToShow      = printConfig["columnToShow"]
    if "columnValueFilter" in printConfig.keys(): 
        columnValueFilter = printConfig["columnValueFilter"]
else:
    f = open(fileLocation,"r")
    header = f.readline()
    f.seek(0)
    configDict = {}
    configDict["Table"] = fileLocation
    colToShow = []
    for colname in header.split():
        colToShow.append(colname)
    configDict["columnToShow"] = colToShow
    columnToShow      = colToShow
    defaultConfigName = fileLocation.split("/")[-1].replace("txt","json")
    if not os.path.exists(defaultConfigName):
        print "Cannot found printConfig json file, writing a new one: %s " % (fileLocation.split("/")[-1].replace("txt","json"))
        newConfig = open(fileLocation.split("/")[-1].replace("txt","json"),"w")
        newConfig.write(json.dumps(configDict))
    else:
        printConfigFile=open(defaultConfigName)
        printConfig       = json.load(printConfigFile)
        columnToShow      = printConfig["columnToShow"]
        if "columnValueFilter" in printConfig.keys():
            columnValueFilter = printConfig["columnValueFilter"]
    
startTime    = datetime.strptime(args.startTime,"%Y-%m-%d %H:%M")
if args.endTime is not None:
    endTime      = datetime.strptime(args.endTime,"%Y-%m-%d %H:%M")
else:
    endTime = None


header       = open(fileLocation).readline().split()
loggerTable  = loadfile(fileLocation,startTime,maxLine,endTime)
#print "Showing column json" 
headerJson = {}
headerJson["columnToShow"] = header
#print json.dumps(headerJson)

makePlots       = True
makePrettyTable = True
table = PrettyTable()
fieldNames = []
graphs     = {}
# Print ouptut columns
output="                       "
for colname in columnToShow:
    if not (colname in header): continue 
    #print colname
    fieldNames.append(colname)
    #Create the graphs
    if not colname =="timestamp":
        g = TGraph()
        g.SetName(colname)
        graphs[colname] = g
    colwidth = max([len(colname)+2,10])
    output +="{:^{width}}".format(colname,width=colwidth)
printRequest(fileLocation,startTime,maxLine,columnValueFilter,endTime)
if not makePrettyTable: 
    print output 
table.field_names = fieldNames


# Print results
for row in loggerTable:
    output = ""
    skip   = False
    if len(columnValueFilter)>0:
       for Filter in columnValueFilter:
           if Filter["logic"]=="exact":
               if not (Filter["value"] == row[Filter["colname"]]): skip=True
           elif Filter["logic"]=="contain":
               if not (Filter["value"] in row[Filter["colname"]]): skip=True
           elif Filter["logic"]==">=":
               if not (float(row[Filter["colname"]]) >= float(Filter["value"])): skip=True
           elif Filter["logic"]=="<=":
               if not (float(row[Filter["colname"]]) <= float(Filter["value"])): skip=True
    if skip : continue
    tableRow = []
    
    timeString  = row["timestamp"].replace("+02:00","").replace("+01:00","")
    t           = convertTimeString(timeString) 
    for colname in columnToShow:
        if not (colname in header): continue        #allow commenting from json
        colwidth = len(row[colname])+2
        output += "{:^{width}}".format(row[colname],width=colwidth)
        try: 
            y = float(row[colname])
            g = graphs[colname]
            g.SetPoint(g.GetN(),t, y)      #only plot floats
        except ValueError:
            pass
        tableRow.append(row[colname])
    table.add_row(tableRow)
    if not makePrettyTable: 
        print output
if makePrettyTable: 
    print table
if makePlots:
    graphROOT = TFile("graphs.root","RECREATE")
    for gName in graphs:
        graphs[gName].Write()
        oneGraph = {}
        oneGraph[gName] = graphs[gName].Clone()
        if oneGraph[gName].GetN()>0:
            makeAllplots(oneGraph, columnValueFilter,gName)
    makeAllplots(graphs, columnValueFilter,"multiGraph")