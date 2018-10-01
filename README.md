# MonLoggerReader
Parse text files from monLogger
1. To prepare a json:

`python writejson.py --fileLocation="pathToTextFile" `

2. Configuration of json
`flist` : list of input monLogger txt files. Need to have the same number of columns within one file. Use `#` to skip loading the files
`columnToShow` : list of columns to be plotted. Use `#` to comment.
`columnValueFiler` : a list of dictionaries with keys "colname","value","operator"
e.g.
```
   "columnValueFilter":[
       {
         "colname":"RBX",
         "value":"HEP20",
         "operator":"contain"
      }
   ]
```

3. Example commands:

`python monlogReader.py  --startTime="2018-08-29 18:00" --printConfig="MON_HCAL_NGRBX_PerHERBX.json" --ymax 1E6 --RBX HEM08`
