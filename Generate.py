#!/usr/bin/python


#sshfs roman@192.168.1.101:/ /home/roman/sftp/


import os
import sys
import  string
from time import gmtime, strftime


HourCount = [[[0 for i in xrange(24)] for i in xrange(31)] for i in xrange(24)]
#path = "sftp://192.168.1.101/home/roman/MetData/ZVPP/Sort"
path = "/home/roman/sftp/home/roman/MetData/ZVPP/Sort/data"
dataVersion = "Bolidozor_14"
StationPrefix = "ZVPP"
year = strftime("%Y", gmtime())

for month in xrange(12):
	for day in xrange(31):
		for hour in xrange(24):
			if month+1 < 10:
				strmonth = '0'+ str(month+1)
			else:
				strmonth= str(month+1)
			if day+1 < 10:
				strday = '0' + str(day+1)
			else:
				strday = str(day+1)
			if hour < 10:
				strhour = '0' + str(hour)
			else:
				strhour = str(hour)
			cesta = path + "/" + str(year) + "/" + strmonth + "/" + strday + "/" + str(year) + strmonth + strday + strhour + "_" + StationPrefix + ".dat"
			#cesta = path + "/" + str(year) + "/" + strmonth + "/" + strday + "/" + str(year) + strmonth + strday + strhour + "_" + StationPrefix + ".dat"
			try:
				f = open(cesta)
				for line in iter(f):
					#print line
					line = line[line.find('_')+1:]
					line = line[line.find('_')+1:]
					line = line[:line.find(';')]
					if line == "met":
						print "METEOR ------------------      ----" , month+1  ,"--" ,day+1 ,"--" ,hour ,"--"
						HourCount[month+1][day+1][hour] += 1
						#print HourCount[month+1][day+1][hour]
					elif line == "fb":
						print "METEOR ------------------ FB"
						HourCount[month][day][hour] += 1
				f.close()
			except IOError:
				print 'Soubor neexistuje: '+ "/" + str(year) + strmonth + strday + strhour + "_" + StationPrefix + ".dat"
				#pass
			#print HourCount[month][day][hour]
pozice = 0
weekavg = 0
outFile = open('GraphData.js','w')
outFile.write('var datasets = {\n\t')
outFile.write('"HourInYear": {\n\t\t')
outFile.write('label: "HourInYear",\n\t\t')
outFile.write('data: [\n\t\t\t')
for month in xrange(12):
	for day in xrange(31):
		for hour in xrange(24):
			pozice += 1
			outFile.write('[')
			outFile.write(str(pozice))
			outFile.write(",")
			outFile.write(str(HourCount[month][day][hour]))
			outFile.write('],')
			if day == 30 and hour == 23:
				outFile.write('\n\t\t\t')
outFile.write(']},\n\n')

pozice = 0
outFile.write('"DayAvgInYear": {\n\t\t')
outFile.write('label: "DayAvgInYear",\n\t\t')
outFile.write('data: [\n\t\t\t')
for month in xrange(12):
	for day in xrange(31):
		for hour in xrange(24):	
			if hour == 0:
				weekavg = 0
			weekavg += HourCount[month][day][hour]
			if hour == 23:
				pozice += 1
				weekavg = weekavg/24
				outFile.write("[")
				value=pozice*24
				outFile.write(str(value))
				outFile.write(",")
				outFile.write(str(weekavg))
				outFile.write("],")
			if day == 30 and hour == 23:
				outFile.write('\n\t\t\t')
outFile.write(']},\n\n')

pozice = 0
outFile.write('"DayMaxinYear": {\n\t\t')
outFile.write('label: "DayMaxinYear",\n\t\t')
outFile.write('data: [\n\t\t\t')
for month in xrange(12):
	for day in xrange(31):
		for hour in xrange(24):	
			if hour == 0:
				weekavg = 0
			if weekavg < HourCount[month][day][hour]:
				weekavg = HourCount[month][day][hour]
			if hour == 23:
				pozice += 1
				outFile.write("[")
				value=pozice*24
				outFile.write(str(value))
				outFile.write(",")
				outFile.write(str(weekavg))
				outFile.write("],")
outFile.write(']},\n\n')

pozice = 0
outFile.write('"DayMininYear": {\n\t\t')
outFile.write('label: "DayMininYear",\n\t\t')
outFile.write('data: [\n\t\t\t')
for month in xrange(12):
	for day in xrange(31):
		for hour in xrange(24):	
			if hour == 0:
				weekavg = 999
			if weekavg > HourCount[month][day][hour]:
				weekavg = HourCount[month][day][hour]
			if hour == 23:
				pozice += 1
				outFile.write("[")
				value=pozice*24
				outFile.write(str(value))
				outFile.write(",")
				outFile.write(str(weekavg))
				outFile.write("],")
outFile.write(']},\n\n')
outFile.write('};')
outFile.close()