"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT license.

MIMIC-III Sepsis Cohort Extraction.

This file is sourced and modified from: https://github.com/matthieukomorowski/AI_Clinician
"""

import argparse
import os

import pandas as pd
import psycopg2 as pg


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", default='postgres', help="Username used to access the MIMIC Database", type=str)
parser.add_argument("-p", "--password", default='t33tass3', help="User's password for MIMIC Database", type=str)
pargs = parser.parse_args()

# Initializing database connection
conn = pg.connect("dbname='mimic' user={0} host='localhost' options='--search_path=mimimciii' password={1}".format(pargs.username,pargs.password))

# Path for processed data storage
exportdir = os.path.join(os.getcwd(),'./processed_files')

"""if not os.path.exists(exportdir):
    os.makedirs(exportdir)"""

query = """
select subject_id, hadm_id, category, description, iserror, text, extract(epoch from charttime) as charttime, extract(epoch from chartdate) as chartdate, extract(epoch from storetime) as storetime 
from mimiciii.noteevents
order by subject_id, hadm_id, charttime
"""

d = pd.read_sql_query(query,conn)
d.to_csv(os.path.join(exportdir, 'note_events_epochdates.csv'),index=False,sep='|')