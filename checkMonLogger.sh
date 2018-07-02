#!/usr/bin/sh

## uHTR files
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_AMCsErrorCount.txt" --startTime="2018-05-07 19:00" --maxLine=5000
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_UHTR_Fibers.txt" --startTime="2018-05-23 05:08" --maxLine=5000  --printConfig="uHTR_fib.json"

## HF files
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHFSlot.txt" --startTime="2017-11-24 00:04" --maxLine=50 --printConfig="PerHFSlot.txt"
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHFFrontEndCrate.txt" --startTime="2018-05-14 13:00" --endTime="2018-05-14 13:10" --maxLine=5000 --printConfig="PerHFFrontEndCrate.json"
#python readMonLogger.py --fileLocation="/nfshome0/kakwok/monLogger/MON_HCAL_NGRBX_PerHFFrontEndCrate-20180504" --startTime="2018-05-04 12:20" --endTime="2018-05-04 12:40" --maxLine=5000 --printConfig="PerHFFrontEndCrate.json"
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHFFrontEndCrate.txt" --startTime="2018-05-23 16:00" --maxLine=5000 --printConfig="PerHFFrontEndCrate.json"
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHFQIECard.txt" --startTime="2018-05-23 16:00" --maxLine=5000 --printConfig="PerHFQIECard.json"

#### HE files
python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHERBX.txt" --startTime="2018-06-30 00:00" --maxLine=2000 --printConfig="MON_HCAL_NGRBX_PerHERBX.json" 
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHEQIE.txt" --startTime="2018-05-28 16:00" --maxLine=500 --printConfig="MON_HCAL_NGRBX_PerHEQIE.json" 
#python readMonLogger.py --fileLocation="/nfshome0/hcalsw/monlog_loc/ALL/MON_HCAL_NGRBX_PerHEQIECard.txt" --startTime="2018-05-28 16:00" --maxLine=500 --printConfig="MON_HCAL_NGRBX_PerHEQIECard.json" 
