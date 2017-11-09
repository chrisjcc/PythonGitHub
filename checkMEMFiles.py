#############################################
#                                           #
#                                           #
#   Write by: Christian Contreras-Campana   #
#   email: christian.contreras@desy.de      #
#   Date: 01.08.2015                        #
#                                           #
#############################################

# Description: Sowftware produce a report of missing files from selectionRoot file 

import os
import sys
import os.path
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Determine if .root file contains corresponding .txt file')

parser.add_argument("-b", '--base_dir', type=str, default="selectionRoot", help='base directory')

args = parser.parse_args()

base_dir = args.base_dir

print('base (absolute path) = ' + base_dir + '\t(' + os.path.abspath(base_dir)) + ')'

text_file = open("filename.dat", "r")
lines = defaultdict(list)

for key in [x.strip('\n') for x in text_file.readlines()]:
    lines[key].append(-999)

for root, subdirs, files in os.walk(base_dir):

    print('--\nroot dir = ' + root)
    list_file_path = os.path.join(root, 'tmp-directory-list.txt')

    with open(list_file_path, 'wb') as list_file:

        for subdir in subdirs:
            print('\t- subdirectory ' + subdir)

        for filename in files:
            file_path = os.path.join(root, filename)

            with open(file_path, 'rb') as f:

                if f.name.find(".root") != -1:
                    tmp = f.name.replace(".root","")
                    element = os.path.split(tmp)[1].replace("ee_","").replace("mumu_","").replace("emu_","")

                    if element in lines.keys():
                        lines[element] = 1

        # Indicate total number of files found                  
        print str(str(sum(x != 1 for x in lines.values())))+" out of "+ str(sum(x == 1 for x in lines.values()))

        # Loop over dictionary of process-key value
        for (key, value) in lines.iteritems():

            # Print process if not found
            if value == -999:
                print  str(key)

        # Indicate total number of files found 
        #print str(str(sum(x == 1 for x in lines.values())))+" out of "+ str(len(lines))

        # Re-initialize dictionary (i.e. map)
        for key in lines:
            lines[key] = -999

    os.remove(list_file_path)

text_file.close()

