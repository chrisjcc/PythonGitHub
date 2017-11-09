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

base_dir = args.base_dir+"/"

print('base (absolute path) = ' + base_dir + '\t(' + os.path.abspath(base_dir)) + ')'

text_file = ["dyee1050","dyee50inf","dymumu1050","dymumu50inf","dytautau1050","dytautau50inf","singleantitop_tw","singletop_tw","ttbarAllhadronic2b","ttbarAllhadronicB","ttbarAllhadronicBbbar","ttbarAllhadronicCcbar","ttbarAllhadronicOther","ttbarDileptonNotau2b_fromDilepton0","ttbarDileptonNotauB_fromDilepton0","ttbarDileptonNotauBbbar_fromDilepton0","ttbarDileptonOnlytau2b_fromDilepton0","ttbarDileptonOnlytauB_fromDilepton0","ttbarDileptonOnlytauBbbar_fromDilepton0","ttbarDileptonPlustauCcbar_fromDilepton0","ttbarDileptonPlustauOther_fromDilepton0","ttbarH125tobbbar","ttbarH125toccbar","ttbarH125togammagamma","ttbarH125togluongluon","ttbarH125totautau","ttbarH125toww","ttbarH125tozgamma","ttbarH125tozz","ttbarNotdilepton2b_fromDilepton0","ttbarNotdilepton2b_fromLjets","ttbarNotdileptonB_fromDilepton0","ttbarNotdileptonB_fromLjets","ttbarNotdileptonBbbar_fromDilepton0","ttbarNotdileptonBbbar_fromLjets","ttbarNotdileptonCcbar_fromDilepton0","ttbarNotdileptonCcbar_fromLjets","ttbarNotdileptonOther_fromDilepton0","ttbarNotdileptonOther_fromLjets","ttbarWjetstolnu","ttbarWjetstoqq","ttbarZtoqq","wtolnu","wwtoall","wztoall","zztoall"]

numOfFiles = {"BTAGDISCR_BPURITY_DOWN" : 46, "BTAGDISCR_BPURITY_UP" : 46, "BTAGDISCR_BSTAT1_DOWN" : 46," BTAGDISCR_BSTAT1_UP" : 46, "BTAGDISCR_BSTAT2_DOWN" : 46, "BTAGDISCR_BSTAT2_UP" : 46, "BTAGDISCR_CERR1_DOWN" : 46, "BTAGDISCR_CERR1_UP" : 46, "BTAGDISCR_CERR2_DOWN" : 46, "BTAGDISCR_CERR2_UP" : 46, "BTAGDISCR_LPURITY_DOWN" : 46, "BTAGDISCR_LPURITY_UP" : 46, "BTAGDISCR_LSTAT1_DOWN" : 46, "BTAGDISCR_LSTAT1_UP" : 46, "BTAGDISCR_LSTAT2_DOWN" : 46, "BTAGDISCR_LSTAT2_UP" : 46, "JER_DOWN": 46, "JER_UP" : 46, "JES_DOWN" : 46, "JES_UP": 46, "Nominal" : 46, "PU_DOWN" : 46, "PU_UP" : 46, "SCALE_DOWN" : 46, "SCALE_UP" : 46, "MESCALE_UP" : 46, "MESCALE_DOWN" : 46, "TRIG_DOWN" : 46, "TRIG_UP" : 46, "LEPT_UP" : 46, "LEPT_DOWN" : 46}

lines = defaultdict(list)

for key in [x.strip('\n') for x in text_file]:
    lines[key].append(-999)

for root, subdirs, files in os.walk(base_dir):

    print('--\n\nroot dir = ' + root)
    list_file_path = os.path.join(root, 'tmp-directory-list.txt')

    with open(list_file_path, 'wb') as list_file:

        # Print the list of sub-directory
        for subdir in subdirs:
            print('\t- subdirectory ' + subdir)

        for filename in files:
            file_path = os.path.join(root, filename)

            # Open of file
            with open(file_path, 'rb') as f:

                if f.name.find(".root") != -1:
                    tmp = f.name.replace(".root","")
                    element = os.path.split(tmp)[1].replace("ee_","").replace("mumu_","").replace("emu_","")

                    if element in lines.keys():
                        lines[element] = 1

        # Indicate total number of files found
        totalNumOfFiles = 0
        if len(root.split('/')) > 1:
            if root.split('/')[1] in numOfFiles.keys():
                totalNumOfFiles = sum(x == 1 for x in lines.values())

                print str(totalNumOfFiles)+" out of "+str(numOfFiles[root.split('/')[1]])+" files found."

                if totalNumOfFiles != numOfFiles[root.split('/')[1]]: 
                     print "Files not found:" 

        # Loop over dictionary of process-key value
        for (key, value) in lines.iteritems():

            # Print process if not found
            if root.split('/')[1] in numOfFiles.keys() and value == -999:
                print "\t"+str(key)+".root"

        # Re-initialize dictionary (i.e. map)
        for key in lines:
            lines[key] = -999

    os.remove(list_file_path)
