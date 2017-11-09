#!/usr/bin/env python

import collections
import re
import os

from optparse import OptionParser

# CODE PURPOSE: To create a comma separated value (csv) file which contains the break down of the nominal values for systematics included below
# RUN EXAMPLE: python systematic_yield_extraction.py -f EventYields_selectionRoot_mvaEventA/Nominal/combined/lumiCorrected_events_step7.txt

# ---- Command line option parsing
parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

# ---- List of systematic uncertainties to process
systematics = [
"BTAGDISCR_BPURITY",
"BTAGDISCR_BSTAT1",
"BTAGDISCR_BSTAT2",
"BTAGDISCR_CERR1",
"BTAGDISCR_CERR2",
"BTAGDISCR_LPURITY",
"BTAGDISCR_LSTAT1",
"BTAGDISCR_LSTAT2",
"JER",
"JES",
"LEPT",
"MEFACSCALE",
"MERENSCALE",
"PU",
"TRIG",
]

syst_nominal={}

# ---- Set up files and directory paths
sub_directories = str(options.filename).split('/')
input_filename  = os.path.basename(options.filename)
output_filename = os.path.splitext(input_filename)[0]+".csv"

# ---- Set input and output file handlers
f_out = open(output_filename, 'a')
f_nom = open(options.filename,'r')

# ---- Read in file from the nominal case
for line in f_nom.xreadlines():

   nominal_values = re.split(':|    \+\-',line)

   if nominal_values[0] == 'Total background' or nominal_values[0] == 'Total MC':
         continue
   try:
      syst_nominal[nominal_values[0]].append({'Nominal': [nominal_values[1]]})
   except KeyError:
      syst_nominal[nominal_values[0]] = {'Nominal': [nominal_values[1]]}

# ----- Loop through list of systematic to extract information from text
for systematic in systematics:

   # ---- Read in file from the up and down variation case
   f_nom_up   = open(sub_directories[0]+"/"+systematic+'_UP'+"/"+sub_directories[2]+"/"+input_filename,'r')
   f_nom_down = open(sub_directories[0]+"/"+systematic+'_DOWN'+"/"+sub_directories[2]+"/"+input_filename,'r')

   for line in f_nom_up.xreadlines():
      nominal_values = re.split(':|    \+\-',line)

      if nominal_values[0] == 'Total background' or nominal_values[0] == 'Total MC':
         continue

      try:
         syst_nominal[nominal_values[0]][systematic].append([nominal_values[1]])
      except KeyError:
         syst_nominal[nominal_values[0]][systematic] = [nominal_values[1]]

   for line in f_nom_down.xreadlines():
      nominal_values = re.split(':|    \+\-',line)

      if nominal_values[0] == 'Total background' or nominal_values[0] == 'Total MC':
         continue

      syst_nominal[nominal_values[0]][systematic].append(nominal_values[1])

   f_nom.close()
   f_nom_down.close()
   f_nom_up.close()

# ---- Print to screen and store information in output file
print 'PROCESS,',
f_out.write('PROCESS,')
for systematic in syst_nominal.values()[0].keys():
   if systematic != 'Nominal':
      print systematic+"_UP,"+systematic+"_DOWN,",
      f_out.write(systematic+"_UP,"+systematic+"_DOWN,")
   else:
      print systematic+",",
      f_out.write(systematic+",")

print
f_out.write("\n")

for process in syst_nominal.keys():
   print process+",",
   f_out.write(process+",")

   for values in syst_nominal[process].values():
      print ",".join(values),',',
      f_out.write(",".join(values)+",")
   print
   f_out.write("\n")

