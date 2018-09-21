#!/usr/bin/env python2

import os

for end in "MP":
    for sector in range(1, 19)+[29,30]:
        rbx = "HE%1s%02d" % (end, sector)
        if rbx in ["HEM15","HEM16","HEM30","HEP29"]: continue   #skip HEM15,16
        cmd = 'python readMonLogger.py --fileLocation="/globalscratch/kakwok/MON_HCAL_NGRBX_PerHERBX-20180919" --startTime="2018-09-14 09:00"  --endTime="2018-09-20 14:00" --maxLine=10000000 --printConfig="./MON_HCAL_NGRBX_PerHERBX.json" --makePlots --RBX %s --odir smezz' % (rbx)
        #cmd = 'python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHERBX.txt" --startTime="2018-09-14 09:00"  --endTime="2018-09-20 14:00" --maxLine=10000000 --printConfig="./MON_HCAL_NGRBX_PerHERBX.json" --makePlots --RBX %s --odir smezz' % (rbx)
        print cmd
        os.system(cmd)
