#/usr/bin/env python2

import argparse
import cProfile
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from datetime import datetime
from ROOT import *
import os

def buildname(elements):
    listTojoin = []
    for el in elements:
        if el is not "":    listTojoin.append(el)
    return "_".join(listTojoin)

def convertTimeString(timeString):
    ts = datetime.strptime(timeString,'%Y-%m-%d %H:%M:%S.%f')
    t  = TDatime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)                           
    return t.Convert()

def getDataFrame(filename,columnToShow,columnValueFilters):
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
    #    df = pd.read_csv(filename,delim_whitespace=True)
    df = pd.read_csv(filename,delim_whitespace=True)
    
    df['timestamp'] = df['timestamp'].apply(lambda x: x.split('+')[0])
    df['timestamp'] = df['timestamp'].apply(lambda x: x.replace('T',' '))
    # filter out extra header rows
    df = df[df.timestamp != 'timestamp']
    #df = df.iloc[:55000]
    # get matplotlib dates
    #df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    #df['dates'] = matplotlib.dates.date2num(df['timestamp'])
    # get ROOT  dates
    df['dates'] = df['timestamp'].apply(convertTimeString)
    # convert to python datetimes
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
 
def makeplots(dfcut,cols,cvf,title,ymin,ymax,png):
    gROOT.SetBatch()
    mg     = TMultiGraph()
    nGraphs= 0
    can = TCanvas("c","c",2400,1600)
    can.SetLogy(1)
    leg = TLegend(0.2,0.3,0.5,0.45)
    for col in cols:
        if not col in dfcut.columns or "timestamp"==col : continue
        x    = np.array(dfcut['dates'],'d')
        try: 
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
        leg.AddEntry(g,col,"lp")
        nGraphs +=1
    filterInfo=""
    for Filter in cvf:
        if "timestamp" in Filter['colname']: continue
        filterInfo += "%s %s "%(Filter['colname'],Filter['value'])
    mg.SetTitle(filterInfo)
    mg.SetName("multigraph")
    #mg.Draw("ap")
    mg.Draw("alp")
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
        os.system("pdftoppm -cropbox -singlefile -rx 400 -ry 300 -png %s %s" % (pdf, title))

def buildselection(df, filters):
    for f in filters:
        if f['operator'] == "==":
            df =  df.loc[ df[f['colname']]==f['value'] ]
        if f['operator'] == ">=":
            df =  df.loc[ df[f['colname']]>=f['value'] ]
        if f['operator'] == "!=":
            df =  df.loc[ df[f['colname']]!=f['value'] ]
        if f['operator'] == "<=":
            df =  df.loc[ df[f['colname']]<=f['value'] ]
    return df
            
def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--printConfig" , help="json file to filter output", required=True)
    parser.add_argument("--startTime"   , help="StartTime to look for lines, format: yyyy-mm-dd HH:MM")
    parser.add_argument("--endTime"     , help="EndTime   to look for lines, format: yyyy-mm-dd HH:MM")
    parser.add_argument("--RBX"         , help="select an RBX "  ,default="")
    parser.add_argument("--crate"       , help="select an crate ",default="")
    parser.add_argument("--ymin"        , help="min y-value on plots", type=float, default=1E-6)
    parser.add_argument("--ymax"        , help="max y-value on plots", type=float, default=1E5)
    parser.add_argument("-o","--odir"   ,dest="odir", help="output path",default="./")
    parser.add_argument("--makeTable"   , help="Print out table to screen ", action='store_true',default=False)
    parser.add_argument("--profile"     , help="Profile this program.", action="store_true", default=False)
    parser.add_argument("--png"         , help="Convert the .pdf to a .png", action="store_true", default=False)
    return parser.parse_args()

def main(args):
    print datetime.now()
    outname = os.path.join(args.odir,buildname([args.crate, args.RBX,"multiGraph",args.printConfig.split("/")[-1].replace(".json",""),args.startTime.split(" ")[0]]))
    
    columnToShow = []
    flist        = []
    if(args.printConfig is not None):
        printConfigFile=open(args.printConfig)
        printConfig       = json.load(printConfigFile)
        columnToShow      = printConfig["columnToShow"]
        if "columnValueFilter" in printConfig.keys(): 
            columnValueFilter = printConfig["columnValueFilter"]
        if "flist" in printConfig.keys(): 
            flist = printConfig["flist"]
            print flist
    
    columnValueFilters=[]
    
    if args.endTime is not None:
        endTime      = datetime.strptime(args.endTime,"%Y-%m-%d %H:%M")
        endTimefilter   = {"colname":"timestamp","value":endTime,"operator":"<="}
        columnValueFilters.append(endTimefilter)
    if args.startTime is not None:
        startTime      = datetime.strptime(args.startTime,"%Y-%m-%d %H:%M")
        startTimefilter   = {"colname":"timestamp","value":startTime,"operator":">="}
        columnValueFilters.append(startTimefilter)
    if args.RBX is not "":
        RBXfilter = {"colname":"RBX","value":args.RBX,"operator":"=="}
        columnValueFilters.append(RBXfilter)
    if args.crate is not "":
        cratefilter = {"colname":"CRATE","value":args.crate,"operator":"=="}
        columnValueFilters.append(cratefilter)
    
    df_list = []
    for f in flist:
        if f[0]=="#": continue
        df_list.append( getDataFrame(f,columnToShow,columnValueFilters))
    
    
    frames = pd.concat( df_list )
    frames.sort_values( by='dates')
    
    if args.makeTable:
        print frames
    
    dfcut = buildselection(frames,columnValueFilters) 
    print outname
    outf    = TFile(outname+".root","RECREATE")
    makeplots(dfcut, columnToShow, columnValueFilters, outname, args.ymin, args.ymax, args.png)
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

