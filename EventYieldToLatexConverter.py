#!/usr/bin/python

############################################ 
#                                          #
#   Write by: Christian Contreras-Campana  #
#   email: christian.contreras@desy.de     #
#   Date: 21.06.2015                       #
#                                          #
############################################

''' Description: The following code converts DESY ttH (also Top) analysis text table into latex table format'''

import sys
import argparse
import re
from os import listdir
import glob
from collections import defaultdict
from math import log10, floor
import numpy as npy

from sigfig import *

# ---- Command line parsing options
parser = argparse.ArgumentParser(description='Usage: python EventYieldToLatexConverter.py --CateN "*" --Merge True --Channel mumu --Normalized lumiCorrected')
parser.add_argument('--DirPath', metavar='P', type=str,  default="EventYields",   help='Directory path')
parser.add_argument('--CateN',   metavar='B', type=str,  default="*",             help='Jet category ID # jets, # b-jets: 3, 2 (0), 3,3 (1), 4,2 (2), 4,4 (3)')
parser.add_argument('--Channel', metavar='C', type=str,  default="combined",      help='Dilepton channels: ee, emu, mumu, combined')
parser.add_argument('--StepN',   metavar='S', type=str,  default="7",             help='Step number in analysis cutflow')
parser.add_argument('--Nominal', metavar='N', type=str,  default="Nominal",       help='Nominal, etc.')
parser.add_argument('--Normalized', metavar='L', type=str,  default="lumiCorrected", help='plain (nominal), or lumiCorrected')
parser.add_argument('--Merge',   metavar='M', type=bool, default=False,           help='Jet category merged to single table')
parser.add_argument('--SigFig',  metavar='F', type=int,  default="3",             help='Number of significant figures')
parser.add_argument('--Decimal',  metavar='D', type=bool, default=False,          help='Use decimal print out format')

#  ---- Parse commandline arguments/options
args = parser.parse_args()

#  ---- Load list of files to run over
fileName = str(args.DirPath)+"/"+str(args.Nominal)+"/"+str(args.Channel)+"/"+str(args.Normalized)+"_events_step"+str(args.StepN)+"_cate"+str(args.CateN)+".txt"
print "%File name: "+fileName+"\n"
fileList =  glob.glob(fileName)

#  ---- Set internal variables to use (such as category type)
categoryType = "cate"+str(args.CateN)
count = 0

#  ---- list to store categories, etc.
list0 = []
list1 = []
list2 = []
list3 = []
list4 = []
list5 = []

#  ---- Main containter (pseudo mini-DB)
cell = defaultdict(list)

#  ---- Regular expression designed to parse input text file (break each text line into columns for later access)
regexString = r'(\W*\w*\W*\w*\W*\w*\W*\w*\s*\W*\w*\W*\w*\W*\w*\W*\s*\w*\s*\w*\.*\W*):\s*(\w*.*\w*\+*\-*\w*)\+\-\s*(\w*.*\w*\+*\-*\w*)\s*\((\w*.*\w*)\%\)'

testMatch = re.compile(regexString)


# ---- Include latex header
print '\documentclass[8pt]{article} \n\
\usepackage[letterpaper,textwidth=8.0in,textheight=10.5in]{geometry} \n\
\usepackage{float}   \n\
\usepackage{amsmath} \n\
\usepackage{amssymb} \n\
\usepackage{lscape}  \n\
\usepackage{hyperref} \n\
\usepackage{color}    \n\
\usepackage{graphicx} \n\
\usepackage{pgf}      \n\
\usepackage{siunitx}  \n\
\n\
\pagestyle{empty}  \n\
\n\
% Change below precision/significant figure as desired (defaulted to 6) \n\
\\newcommand*{\sigfig}[1]{\\num[round-mode=figures, scientific-notation=false, round-precision=6]{#1}} \n\
\n\
\\begin{document} \n'

#  ---- Iterate through list of files
for file in fileList:

	# Open a file
	fo = open(file, "r")

	# Match on event category labeling
	pattern = categoryType
        m = re.search(pattern, file)

	# If matched proceed to read file
        if m != None:
		text = str(re.sub(r'\/', '\\\\\/', fo.name))

		# Index to keep track of where total background and signal are stored in the "cell" container
		bkgIndex    = -999
		sigIndex    = -999
		dataIndex   = -999
		bkgCounter  = 0
		sigCounter  = 0
		dataCounter = 0

		print "\\begin{table}[!hbtp] \n\
\\centering \n\
\\small \n\
\\caption["+fo.name+"]{"+str(re.sub(r'_', '\\\\_', text))+"} \n\
\\begin{tabular}{c c c c} \n\
\\hline \n\
\\hline \n\
Sample & Yield & Error & Uncertainty~(\%) \\\\\n\
\\hline \n\
\\hline"      
		# Keep track of the number of processes (i.e data, signal, and backgrounds) to include in the table
		numOfProcess = 0

		# Read lines of files
		for line in fo:
			m = testMatch.match(line)
			tmp = str(re.sub(r'#', '\\\\', str(m.group(1))))
			mGroup1 = str(re.sub(r' ', '\\\\;', tmp))
			list0.append(mGroup1)

			numOfProcess = numOfProcess + 1

			# Following if statment included to break the table format from individual samples and the total yield
			if m.group(1) != "Total background":
				print ("$\\rm %-35s$\t&\t\sigfig{%15.15s} & \sigfig{%-10s}\t&\t$\pm$ \sigfig{%-10s} \\\\" % (mGroup1, m.group(2), m.group(3), m.group(4)))

			else:
				print "\hline"
				print ("$\\rm %-35s$\t&\t\sigfig{%15.15s} & \sigfig{%-10s}\t&\t$\pm$ \sigfig{%-10s} \\\\" % (mGroup1, m.group(2), m.group(3), m.group(4)))

				
			# Store event yield values into respective category
			if args.Merge == True:
				# Keep track of where total background, signal, and data/pseudo-data will be stored in "cell" container
				if m.group(1) != "Total background":
					bkgCounter = bkgCounter+1
				if m.group(1) != "t#bar{t}H":
					sigCounter = sigCounter+1
				if m.group(1) != "Pseudodata" and m.group(1) != "Data":
					dataCounter = dataCounter+1
				if m.group(1) == "Total background":
					bkgIndex = bkgCounter;
				if m.group(1) == "t#bar{t}H":
					sigIndex = sigCounter
				if m.group(1) == "Pseudodata" or m.group(1) == "Data":
					dataIndex = dataCounter

				if str(fo.name).find("cate0") != -1:
					cell["cate0"].append((m.group(2), m.group(3)))
					list1.append(m.group(2))
				elif str(fo.name).find("cate1") != -1:
					cell["cate1"].append((m.group(2), m.group(3)))
					list2.append(m.group(2))
				elif str(fo.name).find("cate2") != -1:
					cell["cate2"].append((m.group(2), m.group(3)))
					list3.append(m.group(2))
				elif str(fo.name).find("cate3") != -1:
					cell["cate3"].append((m.group(2), m.group(3)))
					list4.append(m.group(2))
                                elif str(fo.name).find("cate4") != -1:
					cell["cate4"].append((m.group(2), m.group(3)))
                                        list5.append(m.group(2))
                             
		print "\\hline\n\
\hline\n\
\end{tabular}\n\
\end{table}"
		
		print "\n\n"
		count = count + 1

		# Clearing the latex page is necessary since adding to many tables sequentially can cause the latex compiler not to compile
		if count%15 == 0:
			print "\clearpage"
				
	# Close opend file
	fo.close()

if args.Merge == True and args.CateN == "*":

	# Latex header for jet category mereged table 
	print "\\begin{table}[!hbtp] \n\
\\centering \n\
\\small \n\
\\caption[Event yields for the ee + $e\mu$+ $\mu\mu$ channel]{Event yields for the ee + $e\mu$+ $\mu\mu$ channel (analysis cutflow step "+str(args.StepN)+").}\n\
\\begin{tabular}{c c c c c c} \n\
\\hline \n\
\\hline \n\
Process & 3 jets, 2 b-tags & 3 jets, 3 b-tags & $\geq$~4 jets, 2 b-tags & $\geq$~4 jets, 3 b-tags & $\geq$~4 jets, $\geq$~4 b-tags \\\\\n\
\\hline"

	# Print out merged category table format
	for j in xrange(0,numOfProcess):

		if list0[j] == "Total\;background":
			print "\hline"

		print "$\\rm ",list0[j],"$"," & ",

		for i in xrange(0,5):
			if i < 4:				
				print("$\sigfig{%s} \pm \sigfig{%s}$" % (str(cell["cate"+str(i)][j][0]).strip(), str(cell["cate"+str(i)][j][1]).strip()))," & ",
			else:
				print("$\sigfig{%s} \pm \sigfig{%s}$" % (str(cell["cate"+str(i)][j][0]).strip(), str(cell["cate"+str(i)][j][1]).strip())), " \\\\"

		if list0[j] == "Pseudodata":
			print "\hline"
	# Print S/B value
	if sigIndex != -999 and bkgIndex != -999:
		print "\hline"
		print "$\\rm S/B $ & ",
		for i in xrange(0,5):
			if i < 4:
				# Defaulted to use 6 sig figs
				print "\sigfig{",float(cell["cate"+str(i)][sigIndex][0])/float(cell["cate"+str(i)][bkgIndex][0]),"}", " & ",
			else:
				print "\sigfig{",float(cell["cate"+str(i)][sigIndex][0])/float(cell["cate"+str(i)][bkgIndex][0]),"}"," \\\\"

	# Print Data/B (uncertainty not included)
	if dataIndex != -999 and bkgIndex !=-999:
		print "\hline"
		print "$\\rm",list0[0],"/B $ & ",
		for i in xrange(0,5):
			if i < 4:
				# Defaulted to use 6 sig figs 
				print "\sigfig{",float(cell["cate"+str(i)][dataIndex][0])/float(cell["cate"+str(i)][bkgIndex][0]),"}", " & ",
			else:
				print "\sigfig{",float(cell["cate"+str(i)][dataIndex][0])/float(cell["cate"+str(i)][bkgIndex][0]),"}", " \\\\"

	print "\\hline\n\
\hline\n\
\end{tabular}\n\
\end{table}"

print "\n"
print "\end{document}\n"


