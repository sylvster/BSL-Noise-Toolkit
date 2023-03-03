import sys
import os
import json
import importlib
from obspy.core import UTCDateTime
from datetime import date, timedelta as td

#Import noise toolkit libraries
ntk_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

param_path = os.path.join(ntk_directory, 'param')
lib_path = os.path.join(ntk_directory, 'lib')

sys.path.append(lib_path)
sys.path.append(param_path)

import fileLib as file_lib
import msgLib as msg_lib
import shared

#Declare variables
PERIOD_INDEX = 2
WHITE = "\033[1;37m"
ENDC = '\033[0m'

"""
 Name: ntk_extractPsdPeriod.py - a Python 3 script to extract specified PSD values at specified period spanning across
 multiple different time stamps

 INPUT: the variables in param/extractPsdPeriod.json
 OUTPUT: file in data/psdPr with json variables in the name

 Written by Sylvester Seo
"""

#Read JSON file input
json_path = os.path.join(param_path, 'extractPsdPeriod.json')
json_object = open('param/extractPsdPeriod.json')
json_dict = json.load(json_object)
param_dict = json_dict['psd_parameters']
settings_dict = json_dict['psd_period_settings']


#Format argument into command text
args = ""
for arg in param_dict:
    args += " " + arg + "=" + param_dict[arg]

#Call bin/ntk_computePSD.py
print(f"{WHITE}***************** CALLING COMPUTE PSD *****************{ENDC}")
compute_command = "python bin/ntk_computePSD.py" + args
os.system(compute_command)

#Call bin/ntk_computePsdHour.py
print(f"\n\n{WHITE}***************** CALLING EXTRACT PSD HOUR *****************{ENDC}")
compute_command = "python bin/ntk_extractPsdHour.py" + args
os.system(compute_command)

print(f"\n\n{WHITE}***************** EXTRACTING PERIOD *****************{ENDC}")


#Attempt to read from the extracted PSD File

#Get the date values of extractPsdHour that we are going to read
start_date_time = param_dict['start'].split('T')[0]

end_date_time = param_dict['end'].split('T')[0]

#Set filepath to the extracted PSD hour file
psd_hour_dir, psd_hour_tag = file_lib.get_dir(shared.dataDirectory, shared.psdDirectory, 
                              param_dict['net'], param_dict['sta'], param_dict['loc'], param_dict['chan'])

psd_hour_file = os.path.join(psd_hour_dir, f"{psd_hour_tag}.{start_date_time}.{end_date_time}.{param_dict['xtype']}.txt")

#Begin reading the PSD hour file
if(os.path.exists(psd_hour_file) and os.path.isfile(psd_hour_file)):
    lines = list()
    with open(psd_hour_file) as file:
        for line in file:
            lines.append(line.split())
else:
    code = msg_lib.error(f'Error occurred within ntk_extractPsdHour.py', 2)
    sys.exit(code)

for period in settings_dict['period_value']:
    #Now that data has been retrieved, find the specific period value
    output_lines = list()
    for line in lines:
        if line[PERIOD_INDEX] == period:
            text = '  '.join(line[:PERIOD_INDEX]) + '    ' + line[PERIOD_INDEX + 1]
            output_lines.append(text)

    #Input the data into destination file
    dest_dir, dest_tag = file_lib.get_dir(shared.dataDirectory, 'psdPr', 
                                          param_dict['net'], param_dict['sta'], param_dict['loc'], param_dict['chan'])

    file_lib.make_path(dest_dir)
    dest_tag = f'{dest_tag}.{period}'

    final_destination = os.path.join(dest_dir, dest_tag)
    with open(final_destination, 'w') as file:
        for output in output_lines:
            file.write(f'{output}\n')

#Epilogue
json_object.close()