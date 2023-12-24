import argparse
import pyprind

import numpy as np
import pandas as pd



from scipy.spatial.distance import cdist
from scipy.interpolate import interp1d
from scipy import stats

from fancyimpute import KNN

parser = argparse.ArgumentParser()
parser.add_argument("--process_raw", action='store_true', help="If specified, additionally save trajectories without normalized features")
parser.add_argument("--save_intermediate", action="store_true", help="If specified, save off intermediate tables used to construct final patient table")
pargs = parser.parse_args()

print('Loading processed files created from database using "preprocess.py"')
text           = pd.read_csv('processed_files/note_events.csv',           sep = '|')
demog         = pd.read_csv('processed_files/demog.csv',         sep = '|')

# Initial data manipulations
demog['morta_90'].fillna(0, inplace=True)
demog['morta_hosp'].fillna(0, inplace=True)
demog['elixhauser'].fillna(0, inplace=True)

# Keep only the first icustay of an admission (CRITICAL FIX FROM MATLAB CODE)
demog = demog.drop_duplicates(subset=['admittime','dischtime'],keep='first')

# Get list of all icustayids since that's what we iterate over through the rest of this script
icustayidlist = list(demog.icustay_id.values)

# Calculate the accurate readmission using the demographics data 
# (the SQL code from Komorowski, et al incorrectly cumulatively counts how many icu stays each patient has (preprocess.py:line 414) 
# and does a coarse boolean check if this number is >1). A readmission is now correctly defined by 
# whether the patient has returned to the ICU within 30 days of being previously discharged.

# This is done by grouping all the discharge times for each patient and using them in a comparison 
# with the current row's admission time to see if it's within the 30 day cutoff
subj_dischtime_list = demog.sort_values(by='admittime').groupby('subject_id').apply(lambda df: np.unique(df.dischtime.values)) # Create list of discharge times for each patient (output is a dict keyed by 'subject_id')

def determine_readmission(s, dischtimes=subj_dischtime_list,cutoff=3600*24*30):
    '''
    determine_readmisson evaluates each row of the provided dataframe (designed to operate on the demographics table)
    and chooses whether the current admission occurs within the cutoff of the previous discharge 
    (here, cutoff=30 days is the default)
    '''
    subject, admission, discharge = s[['subject_id','admittime','dischtime']]
    
    # Check for readmission
    subj_stay_idx = np.where(dischtimes[subject]==discharge)[0][0]
    s['re_admission'] = 0
    if subj_stay_idx > 0:
        if (admission - dischtimes[subject][subj_stay_idx-1]) <= cutoff:
            s['re_admission'] = 1
            
    return s
# Apply the above function to determine the appropriate readmissions
demog = demog.apply(determine_readmission,axis=1)

# Fill-in missing ICUSTAY IDs in text
print('Filling-in missing ICUSTAY IDs in text')
bar = pyprind.ProgBar(len(text.index.tolist()))
# Raw Translation
for i in text.index.tolist():
    bar.update()
    if np.isnan(text.loc[i, 'icustay_id']):
        o         = text.loc[i, 'charttime'] 
        subjectid = text.loc[i, 'subject_id']
        hadmid    = text.loc[i, 'hadm_id']
        ii        = demog.index[demog['subject_id'] == subjectid].tolist()
        jj        = demog.index[(demog['subject_id'] == subjectid) & (demog['hadm_id'] == hadmid)].tolist()
        for j in range(len(ii)):
            if (o >= demog.loc[ii[j], 'intime'] - 48*3600) and (o <= demog.loc[ii[j], 'outtime'] + 48*3600):
                text.loc[i,'icustay_id'] = demog.loc[ii[j], 'icustay_id']
            elif len(ii)==1:   # If we cant confirm from admission and discharge time but there is only 1 admission: it's the one!!
                text.loc[i,'icustay_id'] = demog.loc[ii[j], 'icustay_id']

print('Filling-in missing ICUSTAY IDs in bacterio - 2')                
bar = pyprind.ProgBar(len(text.index.tolist()))
for i in text.index.tolist():
    bar.update()
    if np.isnan(text.loc[i, 'icustay_id']):
        subjectid = text.loc[i, 'subject_id']
        hadmid    = text.loc[i, 'hadm_id']
        jj        = demog.index[(demog['subject_id'] == subjectid) & (demog['hadm_id'] == hadmid)].tolist()
        if len(jj) == 1:
            text.loc[i,'icustay_id'] = demog.loc[jj[0], 'icustay_id']