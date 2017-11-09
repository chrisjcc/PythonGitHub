#!/usr/bin/python

############################################ 
#                                          #
#   Write by: Christian Contreras-Campana  #
#   email: christian.contreras@desy.de     #
#   Date: 03.07.2015                       #
#                                          #
############################################

''' Description: The following code converts DESY ttH (also Top) analysis text table into a merged latex table format for the analysis step flow cuts'''

import sys
import argparse
import re
from os import listdir
import glob
from collections import defaultdict
import operator

# ---- Command line parsing options
parser = argparse.ArgumentParser(description='Usage: python EventYieldToLatexConverter.py --CateN "*" --Merge True --Channel mumu --Normalized lumiCorrected')
parser.add_argument('--DirPath', metavar='P', type=str,  default="EventYields",   help='Directory path')
parser.add_argument('--CateN',   metavar='N', type=str,  default="*",             help='Jet category ID # jets, # b-jets: 3, 2 (0), 3,3 (1), 4,2 (2), 4,4 (3)')
parser.add_argument('--Channel', metavar='C', type=str,  default="combined",      help='Dilepton channels: ee, emu, mumu, combined')
parser.add_argument('--StepN',   metavar='S', type=str,  default="*",             help='Step number in analysis cutflow')
parser.add_argument('--Nominal', metavar='L', type=str,  default="Nominal",       help='Nominal, etc.')
parser.add_argument('--Normalized', metavar='N', type=str,  default="lumiCorrected", help='plain (nominal), or lumiCorrected')
parser.add_argument('--Merge',   metavar='M', type=bool, default=False,           help='Jet category merged to single table')
parser.add_argument('--Steps',   metavar='I', type=str,  default="*",             help='Step number in analysis cutflow')
parser.add_argument('--Threshold', metavar='T', type=float, default="1000000.",       help='Indicate threshold to use scientific notation')

# ---- Parse commandline arguments/options
args = parser.parse_args()

# ---- Construct a list which contians the steps of workflow to process (indicated via command line)
listOfSteps=list()
stepsArray=(str(args.Steps).split(","))
for element in stepsArray:
	if re.match(".*-+.*", element):
		array=(element.split("-"))
		for j in xrange(int(array[0]),int(array[1])+1):
			listOfSteps.append(j)
	else:
		listOfSteps.append(element)

# ---- Load list of files to run over
fileName = str(args.DirPath)+"/"+str(args.Nominal)+"/"+str(args.Channel)+"/"+str(args.Normalized)+"_events_step"+str(args.StepN)+".txt"

print "%File name: "+fileName+"\n"
fileList =  glob.glob(fileName)

# ---- Set internal variables to use (such as category type)
stepYields = defaultdict(list)

# ---- Regular expression designed to parse input text file (break each text line into columns for later access)
regexPattern = r'(\W*\w*\W*\w*\W*\w*\W*\w*\s*\W*\w*\W*\w*\W*\w*\W*\s*\w*\s*\w*\.*\W*):\s*(\w*.*\w*\+*\-*\w*)\+\-\s*(\w*.*\w*\+*\-*\w*)\s*\((\w*.*\w*)\%\)'
regexObject = re.compile(regexPattern)

# ---- Iterate through list of files
for file in fileList:

	# If file belongs to one not included in the list of steps to process then skip and not include in the final table printout
	if not any(file.find("step"+str(elem)+".txt") != -1 for elem in listOfSteps):
		continue
			
	# Open a file
	fo = open(file, "r")

	# Match on event category labeling
	if str(args.StepN) == "*":
		steplabel = re.search("(step[0,1,2,3,4,5,6,7,a,b]{1,2}).txt", file)
	else:
		steplabel = re.search("(step"+str(args.StepN)+").txt", file)

	# If matched proceed to read file
        if steplabel != None:

		latextFileName = str(re.sub(r'\/', '\\\\\/', fo.name))
		
		# Read lines of files
		for line in fo:

			match = regexObject.match(line)
			if match != None:

				latexString = str(re.sub(r'#', '\\\\', str(match.group(1))))
				process = str(re.sub(r' ', '\\\\;', latexString))
				value = match.group(2)
				error = match.group(3)
				stepYields[process].append((steplabel.group(1),value,error))
				

	# Close opend file
	fo.close()

# ---- Order the dictionaries value (which is a list of tuples) based on the first element of the type corresponding to the analysis cut flow step
stepYields.update(map(lambda v: (v , sorted(stepYields[v],key=operator.itemgetter(0))), stepYields))

# ---- Latex header document
print '\documentclass[8pt]{article} \n\
\usepackage[letterpaper,textwidth=8.0in,textheight=10.5in]{geometry} \n\
\usepackage{float}   \n\
\usepackage{amsmath} \n\
\usepackage{amssymb} \n\
\usepackage{lscape}  \n\
\usepackage{hyperref} \n\
\usepackage{color}    \n\
\usepackage{graphicx} \n\
\n\
\usepackage{pgf}      \n\
\usepackage{siunitx}  \n\
\n\
\pagestyle{empty}  \n\
\n\
% Set round-precision value to desired precision (defaulted to 6) and round-mode=places to fix decimal precision instead \n\
\\newcommand*{\sigfig}[1]{\\num[round-mode=figures, scientific-notation=false,  round-precision=6]{#1}} \n\
\\newcommand*{\sigNot}[1]{\\num[round-mode=figures, scientific-notation=true, round-precision=6]{#1}} \n\
\\newcommand*{\errorSigfig}[1]{\\num[round-mode=figures, scientific-notation=false,  round-precision=6]{#1}} \n\
\n\
\\begin{document} \n'

# ---- Latex header for jet category mereged table 
print '\\begin{table}[!hbtp] \n\
\\centering \n\
\\tiny \n\
\\caption[Event yields for the '+str(args.Channel)+' channel]{Event yields for the '+str(args.Channel)+' channel for analysis cutflow steps.}\n\
\\begin{tabular}{',
for i in range(0, len(stepYields.values()[0])):
	 print 'l |',
print 'l',
print '} \n\
\\hline \n\
\\hline \n\
Process sample',
# ---- Loops through list of pairs of tuples (step, yield) to select out cut flow step of the analysis chain
for step in [element[0] for element in stepYields.values()[0]]:
        print " & ",step,
print '\\\\\n\
\\hline'

# ---- Print out for Pseudodata and background yields
for process in stepYields:
	
	# Flag used to separate Pseudodata and background printouts
	flag = False
	if str(process).find("Pseudodata") !=-1:
		print '$\\rm '+process+'$',
		for step, value, error in stepYields[process]:
			if float(value) >= args.Threshold:
				print(" & $\sigNot{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
			else:
				print(" & $\sigfig{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
		print '\\\\'
		flag = True
	if flag == True:
		print '\\hline'
		flag = False
	
	if "Total" not in process and  "Pseudodata" not in process:
		print '$\\rm '+process+'$',
                for step, value, error in stepYields[process]:
			if float(value) >= args.Threshold:
                                print(" & $\sigNot{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
			else:
				print(" & $\sigfig{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
		print '\\\\'

print '\\hline' 

# ---- Printout for total MC and background yields
for process in stepYields:

	if "Total" in process:
		print '$\\rm '+process+'$',
                for step, value, error in stepYields[process]:
			if float(value) >= args.Threshold:
                                print(" & $\sigNot{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
			else:
				print(" & $\sigfig{%s} \\pm \errorSigfig{%s}$ " % (str(value).strip(), str(error).strip())),
		print '\\\\'

# ---- Table footer
print '\\hline\n\
\hline\n\
\end{tabular}\n\
\end{table}'

# ---- End latext document
print "\n"
print "\end{document}\n"

