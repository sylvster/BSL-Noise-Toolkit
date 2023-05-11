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
import tsLib as ts_lib
import utilsLib as utils_lib
import shared

#Declare variables
DATE_INDEX = 0
TIME_INDEX = 1
PERIOD_INDEX = 2
VALUE_INDEX = 3
WHITE = "\033[1;37m"
ENDC = '\033[0m'

"""
 Name: ntk_autoPSD.py - a Python 3 script to extract specified PSD values at specified period spanning across
 multiple different time stamps

 INPUT: the variables in param/autoPSD.json
 OUTPUT: file in data/psdPr with json variables in the name

 Written by Sylvester Seo
"""

#Read JSON file input
json_path = os.path.join(param_path, 'autoPSD.json')
json_object = open('param/autoPSD.json')
json_dict = json.load(json_object)
param_dict = json_dict['psd_parameters']
settings_dict = json_dict['psd_period_settings']

#Define required variables
data_directory = shared.dataDirectory
if(param_dict['directory'] != 'None'):
    data_directory = param_dict['directory']

#Check for valid network and station combos
current_instruction = 0
for request_network in param_dict['net']:
    for request_station in param_dict['sta']:
        request_query = utils_lib.get_fedcatalog_url(request_network, request_station, param_dict['loc'], 
                                                    param_dict['chan'], param_dict['start'], param_dict['end'])
        fedcatalog_url = f'{shared.fedcatalog_url}{request_query}'
        try:
            utils_lib.read_url(fedcatalog_url)
        except:
            continue
        print(f"[{current_instruction}] {request_network}.{request_station}.{param_dict['loc']}.{param_dict['chan']}")
        current_instruction += 1

        #Format argument into command text
        args = ""
        for arg in param_dict:
            if(arg == 'net'):
                args += " " + arg + "=" + request_network
            elif(arg == 'sta'):
                args += " " + arg + "=" + request_station
            else:
                args += " " + arg + "=" + param_dict[arg]

        #Call bin/ntk_computePSD.py
        print(f"{WHITE}***************** CALLING COMPUTE PSD *****************{ENDC}")
        compute_command = "python bin/super_test.py" + args
        print(compute_command)
        os.system(compute_command)

        #Call bin/ntk_computePsdHour.py
        print(f"\n\n{WHITE}***************** CALLING EXTRACT PSD DAY *****************{ENDC}")
        compute_command = "python bin/ntk_extractPsdDay.py" + args
        os.system(compute_command)

        print(f"\n\n{WHITE}***************** EXTRACTING PERIOD *****************{ENDC}")


        #Attempt to read from the extracted PSD File

        #Get the date values of extractPsdHour that we are going to read
        start_date_time = param_dict['start']
        start_date = start_date_time.split('T')[0]
        utc_start_date = UTCDateTime(start_date)

        end_date_time = param_dict['end']
        end_date = end_date_time.split('T')[0]
        utc_end_date = UTCDateTime(end_date)

        #Set filepath to the extracted PSD hour file
        psd_hour_dir, psd_hour_tag = file_lib.get_dir(data_directory, shared.psdDirectory, 
                                    request_network, request_station, param_dict['loc'], param_dict['chan'])

        #Begin looping through each day requested
        utc_curr_date = utc_start_date
        lines = list()
        while(utc_curr_date <= utc_end_date):

            curr_date = str(utc_curr_date).split('T')[0]

            psd_hour_file = os.path.join(psd_hour_dir, f"{psd_hour_tag}.{curr_date}.{param_dict['window_length']}.{param_dict['xtype']}.txt")

            #Begin reading the PSD hour file
            if(os.path.exists(psd_hour_file) and os.path.isfile(psd_hour_file)):
                with open(psd_hour_file) as file:
                    for line in file:
                        lines.append(line.split())
            else:
                print('Error occurred within ntk_extractPsdDay.py, skipping...')
                utc_curr_date += 24 * 3600
                continue

            #Increment the current date
            utc_curr_date += 24 * 3600

        for period in settings_dict['period_value']:
            #Now that data has been retrieved, find the closest period value
            output_data = list()
            min_dist = None
            closest_period_line = None
            prev_time = None
            for line in lines:
                curr_time = line[DATE_INDEX] + "T" + line[TIME_INDEX]
                curr_dist = abs(float(period) - float(line[PERIOD_INDEX]))
                if(prev_time != curr_time):
                    if(not closest_period_line is None):
                        output_data.append(closest_period_line)
                    prev_time = curr_time
                    min_dist = curr_dist
                    closest_period_line = line
                else:
                    if(min_dist is None or min_dist >= curr_dist):
                        min_dist = curr_dist
                        closest_period_line = line
            
            #If output data has no lines, exit
            if(len(output_data) == 0):
                print("No data found within the computed PSD files, skipping...")
                continue

            output_data.append(closest_period_line)

            #Input the data into destination file
            dest_dir, dest_tag = file_lib.get_dir(data_directory, 'psdPr', 
                                                request_network, request_station, param_dict['loc'], param_dict['chan'])

            file_lib.make_path(dest_dir)
            dest_tag = f'{dest_tag}.{period}'

            final_destination = os.path.join(dest_dir, dest_tag) + ".txt"

            #Check that the settings are not overwrite
            if not settings_dict['overwrite'] and os.path.exists(final_destination):
                previous_lines = list()
                with open(final_destination, 'r') as file:
                    for line in file:
                        previous_lines.append(line.split())
                if len(previous_lines) > 0:
                    first_date = UTCDateTime(previous_lines[0][DATE_INDEX])
                    last_date = UTCDateTime(previous_lines[len(previous_lines) - 1][DATE_INDEX])
                    curr_first_date = UTCDateTime(output_data[0][DATE_INDEX])
                    curr_last_date = UTCDateTime(output_data[len(output_data) - 1][DATE_INDEX])
                    if curr_first_date < first_date:
                        output_data = output_data + previous_lines
                    elif curr_first_date > last_date:
                        output_data = previous_lines + output_data
                    else:
                        minIndex, maxIndex = len(previous_lines), 0
                        for index in range(len(previous_lines)):
                            date_at_index = UTCDateTime(previous_lines[index][DATE_INDEX])
                            if(curr_first_date <= date_at_index and minIndex > index):
                                minIndex = index
                            if(curr_last_date >= date_at_index and maxIndex < index):
                                maxIndex = index
                        output_data = previous_lines[:minIndex] + output_data + previous_lines[(maxIndex+1):]

            
            #Write to file
            output_lines = list()
            for data in output_data:
                text = '  '.join(data[:VALUE_INDEX]) + '    ' + data[VALUE_INDEX]
                output_lines.append(text)

            with open(final_destination, 'w') as file:
                for output in output_lines:
                    file.write(f'{output}\n')
                    



        #Epilogue
        json_object.close()

if(current_instruction == 0):
    code = msg_lib.error(f'Invalid input of networks and stations. Confirm that at least one of the network-station permutations have a valid FDSN station', 2)
    sys.exit(code)