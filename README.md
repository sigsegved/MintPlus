# MintPlus
A python CLI to group expenses from Mint for one or more person and create a group summary.


```
Usage: MintPlus -p <Path> -n <Names>
	 -p : Base Path where the csv file exist
	 -n : Name of people whose accounts are being consolidated
	      There should be a file for every name provided here under the base path.
	      For ex : MintPlus -p /tmp/ -n tom,ana should have two files /tmp/tom.csv and /tmp/ana.csv 
	 -s : Start date of the report date in MM/DD/YYYY format. 
	 -e : End date of the report date in MM/DD/YYYY format.
```

Example : 

`main.py -p /tmp/ -n tom,ana -s 01/01/2018 -e 12/31/2018`

MintPlus will look for two files named /tmp/tom.csv and /tmp/ana.csv. It will print a combined expense summary. 
