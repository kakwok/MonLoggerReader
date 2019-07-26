#!/usr/bin/env python2

import argparse
import cProfile
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from datetime import datetime
import os,sys

from ROOT import PyConfig
PyConfig.IgnoreCommandLineOptions = True
from ROOT import *

#Return a list of all RBX names
def getAllRBXes():
    rbxes =[]
    for end in "MP":
        for sector in range(1, 19)+[29,30]:
            rbx = "HE%1s%02d" % (end, sector)
            if rbx in ["HEM15","HEM16","HEM30","HEP29"]: continue   #skip HEM15,16
            rbxes.append(rbx)
    return rbxes


def buildname(elements):
    listTojoin = []
    for el in elements:
        if el is not "":    listTojoin.append(el)
    return "_".join(listTojoin)

def convertTimeString(timeString):
    try:
        ts = datetime.strptime(timeString,'%Y-%m-%d %H:%M:%S.%f')
        t  = TDatime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)                           
    except ValueError :
        print "Value error: trying to convert this string to timestamp:", timeString
    return t.Convert()

def getDataFrame(filename,columnToShow,columnValueFilters,args):
    # TODO: load only the columns we are interested in.
    #if columnToShow is not []:
    #    filterKeys =[]
    #    colToSelect = []
    #    for fil in columnValueFilters:
    #        filterKeys.append(fil['colname'])
    #    print "filterKeys: ",filterKeys
    #    for col in columnToShow:
    #        if not "#" in col:
    #            colToSelect.append(col)
    #        elif col.replace("#","") in filterKeys:
    #            colToSelect.append(col.replace("#",""))
    #    print "colToselect",colToSelect 
    #    df = pd.read_csv(filename,delim_whitespace=True,usecols=colToSelect)
    #else:
    #    print columnToShow
    if not args.notMonLog:
        # to get pandas to infer types correctly, we use the "comment" option of read_csv to ignore all lines
        #    starting with 't' for 'timestamp'. Then we have no header lines in the file.
        # to get the headers set correctly, we read them from the first line of the txt file.
        # the comment option, unfortunately, can only be a single character.
        # the first column should always be 'timestamp' and start with a number. this is basically enforced in monlogger.
        with open(filename) as f:
            first_line = f.readline()
        headerNamesList = first_line.split()
        df = pd.read_csv(filename,delim_whitespace=True,comment='t',names=headerNamesList)
        
        df['timestamp'] = df['timestamp'].apply(lambda x: x.split('+')[0])
        df['timestamp'] = df['timestamp'].apply(lambda x: x.replace('T',' '))
        #df = df.iloc[:55000]
        # get matplotlib dates
        #df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
        #df['dates'] = matplotlib.dates.date2num(df['timestamp'])
        # get ROOT  dates
        df['dates'] = df['timestamp'].apply(convertTimeString)
        # convert to python datetimes
        df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    else:
        df = pd.read_csv(filename,sep='\t')
        df = df[df.timestamp != 'timestamp']
        df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    
    return df

def makeplots_matplotlib(df,cols,cvf,title,ymin,ymax):
    colors =""
    #f = plt.figure()
    #ax = plt.gca()
    f,ax = plt.subplots()
    colors=['black','red','blue','yellow','green']
    ax.set_color_cycle(colors)
    for col in cols:
        if not col in df.columns or "timestamp"==col : continue
        try: 
            plt.plot_date(df['dates'],df[col],label=col )
        except ValueError:
            print "Cannot covert column %s"%col
            continue
    plt.yscale('log')
    plt.ylim(ymin, ymax)
    plt.show()
    ax.legend(loc='best')
    plt.savefig("test.pdf")
 
def makeplots(dfcut,cols,cvf,title,ymin,ymax,png,diff,zero,liny,gopt):
    gROOT.SetBatch()
    mg     = TMultiGraph()
    nGraphs= 0
    can = TCanvas("c","c",2400,1600)
    can.SetLogy(not liny)
    leg = TLegend(0.2,0.3,0.5,0.45)
    for col in cols:
        if not col in dfcut.columns or "timestamp"==col : continue
        if diff and not(dfcut[col].dtype==np.float64 or dfcut[col].dtype==np.int64): continue # filter columns without diff
        x    = np.array(dfcut['dates'],'d')
        try: 
            if diff:
                y    = np.array(dfcut[col+"_diff"],'d')
            elif zero:
                y    = np.array(dfcut[col],'d')
                for i in reversed(range(len(y))):
                    y[i] -= y[0]
            else:
                y    = np.array(dfcut[col],'d')
        except ValueError:
            print "Cannot covert column %s"%col
            continue

        g = TGraph(len(x),x,y)
        if g.GetN()==0:continue
        mg.Add(g)
        g.SetLineColor(nGraphs+1)
        g.SetFillColor(nGraphs+1)
        g.SetMarkerColor(nGraphs+1)
        g.SetMarkerStyle(kFullCircle)
        g.SetMarkerSize(0.5)
        g.Write()
        if diff:
            leg.AddEntry(g,col+"_diff","lp")
        else:
            leg.AddEntry(g,col,"lp")
        nGraphs +=1
    filterInfo=""
    for Filter in cvf:
        if "timestamp" in Filter['colname']: continue
        filterInfo += "%s %s "%(Filter['colname'],Filter['value'])
    mg.SetTitle(filterInfo)
    mg.SetName("multigraph")
    mg.Draw(gopt)
    mg.SetMinimum(ymin)
    mg.SetMaximum(ymax)
    mg.GetXaxis().SetTimeDisplay(1)
    mg.Write()
    leg.SetBorderSize(0)
    leg.Draw("same")
    can.SetTickx()
    can.SetTicky()
    pdf = '%s.pdf' % title
    can.SaveAs(pdf)
    if png:
        os.system("pdftoppm -cropbox -singlefile -rx 300 -ry 300 -png %s %s" % (pdf, title))
        print "png file %s.png has been created." % title

def buildselection(df, filters):
    dfcut = df.copy()
    for f in filters:
        if f['operator'] == "==":
            dfcut =  dfcut.loc[ dfcut[f['colname']]==f['value'] ]
        if f['operator'] == ">=":
            dfcut =  dfcut.loc[ dfcut[f['colname']]>=f['value'] ]
        if f['operator'] == "!=":
            dfcut =  dfcut.loc[ dfcut[f['colname']]!=f['value'] ]
        if f['operator'] == "<=":
            dfcut =  dfcut.loc[ dfcut[f['colname']]<= f['value'] ]
    return dfcut
            
def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--printConfig" , help="json file to filter output", required=True)
    parser.add_argument("--startTime"   , help="StartTime to look for lines, format: yyyy-mm-dd HH:MM")
    parser.add_argument("--endTime"     , help="EndTime   to look for lines, format: yyyy-mm-dd HH:MM")
    parser.add_argument("--RBX"         , help="select an RBX "  ,default="")
    parser.add_argument("--RBXes"       , help="Loop all RBXes", action="store_true", default=False)
    parser.add_argument("--crate"       , help="select an crate ",default="")
    parser.add_argument("--slot"        , help="select a slot", default="")
    parser.add_argument("--fiber"       , help="select a fiber", default="")
    parser.add_argument("--ymin"        , help="min y-value on plots", type=float, default=1E-6)
    parser.add_argument("--ymax"        , help="max y-value on plots", type=float, default=1E5)
    parser.add_argument("--ylin"        , help="linear y axis", action="store_true", default=False)
    parser.add_argument("-o","--odir"   ,dest="odir", help="output path",default="./")
    parser.add_argument("--makeTable"   , help="Print out table to screen ", action='store_true',default=False)
    parser.add_argument("--profile"     , help="Profile this program.", action="store_true", default=False)
    parser.add_argument("--png"         , help="Convert the .pdf to a .png", action="store_true", default=False)
    parser.add_argument("--diff"        , help="plot the diff of columns", action="store_true", default=False)
    parser.add_argument("--notMonLog"   , help="do not convert monLogger timestamp", action="store_true", default=False)
    parser.add_argument("--zero"        , help="subtract first value from all subsequent points", action="store_true", default=False)
    parser.add_argument("--gopt"        , help="graphical options", default="alp")
    return parser.parse_args()

def plotdataframe(frames,args,columnToShow,columnValueFilters,outname):
    #outf    = TFile(outname+".root","RECREATE")
    dfcut = buildselection(frames,columnValueFilters) 
    if dfcut.empty:
        print "No entries in the table fits the requirements:"
        for f in columnValueFilters:
            print f['colname'],f['operator'],f['value']
        sys.exit()
    else:
        if args.makeTable:
            colprint=[]
            for col in columnToShow:
                if  col in dfcut.columns : 
                    if args.diff:
                        if (dfcut[col].dtype==np.float64 or dfcut[col].dtype==np.int64):
                           dfcut[col+"_diff"] = dfcut[col].diff()              # make a new diff column
                           dfcut.fillna(0)
                           dfzs              = dfcut[dfcut[col+"_diff"]!=0]             # Zero-suppressd file 
                           colprint.append(col+"_diff") #print only those column exists in the table   
                    else:
                        colprint.append(col) #print only those column exists in the table   
            dfprint = dfcut[colprint]
            print dfprint
            dfprint.to_csv(outname+".txt",sep='\t')
            if args.diff:
                dfzs.to_csv(outname+"_diff.txt", sep='\t')   #Zero-suppressed file
        if args.diff:
            for col in columnToShow:
                if not col in dfcut.columns or "timestamp"==col : continue 
                if (dfcut[col].dtype==np.float64 or dfcut[col].dtype==np.int64):
                    dfcut[col+"_diff"] = dfcut[col].diff()              # make a new diff column
                    dfcut.fillna(0)
                else:
                    print "columne: %s  is not int/float, not performing diff."%col
        makeplots(dfcut, columnToShow, columnValueFilters, outname,
                  args.ymin, args.ymax, args.png, args.diff, args.zero, args.ylin, args.gopt)
    #outf.Close()

def outfilename(args):
    items = []
    if args.RBX:
        items.append(args.RBX)
    if args.crate:
        items.append("Crate"+args.crate)
    if args.slot:
        items.append("Slot"+args.slot)
    if args.fiber:
        items.append("Fiber"+args.fiber)

    items += ["multiGraph",args.printConfig.split("/")[-1].replace(".json","")]

    if args.startTime:
        items.append(args.startTime.split(" ")[0])
    if args.zero:
        items.append("zero")
    return os.path.join(args.odir, buildname(items))


def main(args):
    print datetime.now()

    columnToShow = []
    flist        = []
    columnValueFilters=[]
    if(args.printConfig is not None):
        printConfigFile=open(args.printConfig)
        printConfig       = json.load(printConfigFile)
        columnToShow      = printConfig["columnToShow"]
        if "columnValueFilter" in printConfig.keys(): 
            columnValueFilters = printConfig["columnValueFilter"]
        if "flist" in printConfig.keys(): 
            flist = printConfig["flist"]
            print flist
   
    baseFilters =columnValueFilters
    
    if args.endTime is not None:
        endTime      = datetime.strptime(args.endTime,"%Y-%m-%d %H:%M")
        endTimefilter   = {"colname":"timestamp","value":endTime,"operator":"<="}
        columnValueFilters.append(endTimefilter)
        baseFilters.append(endTimefilter)
    if args.startTime is not None:
        startTime      = datetime.strptime(args.startTime,"%Y-%m-%d %H:%M")
        startTimefilter   = {"colname":"timestamp","value":startTime,"operator":">="}
        columnValueFilters.append(startTimefilter)
        baseFilters.append(startTimefilter)
    if args.RBX is not "":
        RBXfilter = {"colname":"RBX","value":args.RBX,"operator":"=="}
        columnValueFilters.append(RBXfilter)
    if args.crate is not "":
        cratefilter = {"colname":"CRATE","value":int(args.crate),"operator":"=="}
        columnValueFilters.append(cratefilter)
    if args.slot is not "":
        slotfilter = {"colname":"SLOT","value":int(args.slot),"operator":"=="}
        columnValueFilters.append(slotfilter)
    if args.fiber is not "":
        fiberfilter = {"colname":"FIBER","value":int(args.fiber),"operator":"=="}
        columnValueFilters.append(fiberfilter)
    
    df_list = []
    for f in flist:
        if f[0]=="#": continue
        df_list.append( getDataFrame(f,columnToShow,columnValueFilters,args))
    
    
    frames = pd.concat( df_list )
    frames.sort_values( by='dates')
    
    if not args.RBXes:
        plotdataframe(frames,args,columnToShow,columnValueFilters,outfilename(args))
    else:
        RBXes     = getAllRBXes()
        loopfilter = baseFilters
        for RBX in RBXes: 
            print "Making plots for RBX= ",RBX
            RBXfilter = {"colname":"RBX","value":RBX,"operator":"=="}
            loopfilter.append(RBXfilter)
            print loopfilter
            plotdataframe(frames,args,columnToShow,loopfilter,outfilename(args))
            loopfilter.pop()
    # TODO: implement matplotlib function to make nice-looking plots
    #makeplots_matplotlib(dfcut, columnToShow, columnValueFilters, "test", args.ymin, args.ymax)
    print datetime.now()


if __name__ == "__main__":
    args = parsed_args()

    if args.profile:
        pr = cProfile.Profile()
        pr.runcall(main, args)
        pr.print_stats("time")
    else:
        main(args)

