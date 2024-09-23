# Import and compare different AIFs

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from matplotlib import colors as mcolors
#from PIL import Image
#from scipy import ndimage
import re

print("Hello World")

# path to AIF values
manual_aif_values_dir = '/media/network_mriphysics/USC-PPG/bids_test/derivatives/dceprep-manualAIF'
auto_aif_values_dir = '/media/network_mriphysics/USC-PPG/bids_test/derivatives/dceprep-autoAIF_testset'

# path to subject IDs to compare
id_list_dir = '/media/network_mriphysics/USC-PPG/AI_training/weights/new_GRASP_masks/train_set.txt'
#training_images_dir = '/media/network_mriphysics/USC-PPG/AI_training/loos_model/'

# path to output directory
output_dir = '/media/network_mriphysics/USC-PPG/AI_training/results/test_score'


# read in the subject IDs
with open(id_list_dir) as f:
    id_list = f.readlines()

aif_values = {}

# find each files from subject IDs
for id in id_list:
    id = id.strip()
    #print(id)

    # if id contains "LLU" or "Public", skip
    if re.search(r'LLU', id) or re.search(r'Public', id):
        continue

    # use a regular expression to check id for a 6 digit number and save it as a subject ID
    subject_id = re.search(r'\d+', id).group(0)
    subject_id = 'sub-' + subject_id
    # search id for "1st"
    if re.search(r'1st', id) or re.search(r'ses-01', id):
        session_id = 'ses-01'
    elif re.search(r'2nd', id) or re.search(r'ses-02', id):
        session_id = 'ses-02'
    elif re.search(r'3rd', id) or re.search(r'ses-03', id):
        session_id = 'ses-03'
    elif re.search(r'4th', id) or re.search(r'ses-04', id):  
        session_id = 'ses-04'

    # AIF comparison
    manual_aif_file = os.path.join(manual_aif_values_dir, subject_id, session_id,'dce','B_dcefitted_R1info.log')
    auto_aif_file = os.path.join(auto_aif_values_dir, subject_id,session_id,'dce','B_dcefitted_R1info.log')

    # check if the files exist
    if not os.path.exists(manual_aif_file):
        #print(f"Manual AIF file for {subject_id} does not exist.")
        continue
    #if not os.path.exists(auto_aif_file):
        #print(f"Auto AIF file for {subject_id} does not exist.")
        #continue

    # read in the AIF values
    # Extract the section after "AIF mmol:"
    with open(manual_aif_file) as f:
        manual_aif_text = f.readlines()
    #with open(auto_aif_file) as f:
    #    auto_aif_text = f.readlines()
    
    manual_aif_section = re.search(r'AIF mmol:\s*(.*?)(?:\n\n|Finished B)', ''.join(manual_aif_text), re.DOTALL).group(1)
    #auto_aif_section = re.search(r'AIF mmol:\s*(.*?)(?:\n\n|Finished B)', ''.join(auto_aif_text), re.DOTALL).group(1)

    # Find all floating-point numbers in the extracted section
    manual_aif_float = np.array([float(num) for num in re.findall(r'\d+\.\d+', manual_aif_section)])
    #auto_aif_float = np.array([float(num) for num in re.findall(r'\d+\.\d+', auto_aif_section)])
    auto_aif_float = np.zeros(len(manual_aif_float))

    #print(manual_aif_float)
    #print(auto_aif_float)
    
    # save id, manual_aif_float, and auto_aif_float in a dictionary
    aif_values[subject_id] = {
        'session_id': session_id,
        'manual_aif_float': manual_aif_float,
        'auto_aif_float': auto_aif_float
    }

    # Ktrans comparison
    manual_ktrans_file = os.path.join(manual_aif_values_dir, subject_id, session_id,'dce',subject_id+'_'+session_id+'_Ktrans.nii')  
    auto_ktrans_file = os.path.join(auto_aif_values_dir, subject_id,session_id,'dce',subject_id+'_'+session_id+'_Ktrans.nii')

    # check if the files exist
    if not os.path.exists(manual_ktrans_file):
        print(f"Manual Ktrans file for {subject_id} does not exist.")
        continue
    #if not os.path.exists(auto_ktrans_file):
    #    print(f"Auto Ktrans file for {subject_id} does not exist.")
    #    continue

    # Load image
    manual_volume_img = nib.load(manual_ktrans_file)
    manual_volume_data = manual_volume_img.get_fdata()
    #auto_volume_img = nib.load(auto_ktrans_file)
    #auto_volume_data = auto_volume_img.get_fdata()
    auto_volume_data = np.zeros(manual_volume_data.shape)

    # append the Ktrans values to the dictionary
    aif_values[subject_id]['manual_ktrans'] = manual_volume_data
    aif_values[subject_id]['auto_ktrans'] = auto_volume_data

    
print(f"Number of subjects: {len(aif_values)}")

# Get all items in the dictionary
manual_mean_list = []
auto_mean_list = []
manual_max_list = []
auto_max_list = []
manual_ktrans_list = []
auto_ktrans_list = []

for key, value in aif_values.items():
    #print(f"Subject ID: {key}")
    #print(f"Session ID: {value['session_id']}")
    #print(f"Manual AIF Float: {value['manual_aif_float']}")
    #print(f"Auto AIF Float: {value['auto_aif_float']}")
    #print()

    manual_mean = np.mean(value['manual_aif_float'])
    manual_mean_list.append(manual_mean)
    auto_mean = np.mean(value['auto_aif_float'])
    auto_mean_list.append(auto_mean)
    manual_max = value['manual_aif_float'].max()
    manual_max_list.append(manual_max)
    auto_max = value['auto_aif_float'].max()
    auto_max_list.append(auto_max)

    #print(f"Manual Mean: {manual_mean}")
    #print(f"Auto Mean: {auto_mean}")
    #print(f"Manual Max: {manual_max}")
    #print(f"Auto Max: {auto_max}")

    #check if dictionary contains Ktrans values
    if 'manual_ktrans' in value and 'auto_ktrans' in value:
        #get mean value excluding zeros
        manual_ktrans = np.array(value['manual_ktrans'])
        if np.count_nonzero(manual_ktrans) == 0:
            manual_ktrans_list.append(0)
            print(f"Manual Ktrans for {key} is all zeros.")
        else:
            manual_ktrans_mean = np.mean(manual_ktrans[manual_ktrans != 0])
            manual_ktrans_list.append(manual_ktrans_mean)
        auto_ktrans = np.array(value['auto_ktrans'])
        if np.count_nonzero(auto_ktrans) == 0:
            auto_ktrans_list.append(0)
        else:
            auto_ktrans_mean = np.mean(auto_ktrans[auto_ktrans != 0])
            auto_ktrans_list.append(auto_ktrans_mean)

# make a scatter plot of manual_mean_list and auto_mean_list
plt.figure()
plt.scatter(manual_mean_list, auto_mean_list)
plt.xlabel('Manual Mean')
plt.ylabel('Auto Mean')
plt.title('Mean AIF Values')


# make a scatter plot of manual_ktrans_list and auto_ktrans_list
plt.figure()
plt.scatter(manual_ktrans_list, auto_ktrans_list)
plt.xlabel('Manual Ktrans')
plt.ylabel('Auto Ktrans')
plt.title('Ktrans Values')
plt.xlim(0, 0.006)
plt.show()


