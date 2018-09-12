#!/usr/bin/env python2

import os

for end in "MP":
    for sector in range(1, 19):
        rbx = "HE%1s%02d" % (end, sector)
        if rbx in ["HEM15","HEM16"]: continue   #skip HEM15,16
        cmd = 'python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHERBX.txt.11092018" --startTime="2018-07-11 14:00"  --endTime="2018-09-11 14:00" --maxLine=10000000 --printConfig="./3V3/3V3.json" --makePlots --RBX %s --ymin 1E-3 --ymax 10 --odir 3V3' % (rbx)
        print cmd
        os.system(cmd)
