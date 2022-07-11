#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import csv
import sys
import pprint
import pandas as pd
import pickle as pkl
from os.path import join
from os import listdir, path
from tqdm.notebook import tqdm
from clinical_sectionizer import TextSectionizer


# In[2]:


section_guidelines = {'discharge summary': {'sexual_and_social_history': {'social history:': 76, 'sh:': 8}, 'physical_exam': {'physical exam:': 93, 'physical examination': 26, 'pe:': 9, 'review of systems:': 1, 'exam:': 2}, 'observation_and_plan': {'a:': 80, 'discharge diagnosis:': 148, 'impression:': 114, 'diagnosis:': 29, 'assessment/plan:': 3, 'diagnoses:': 20, 'a/p:': 24, 'discharge diagnoses:': 22, 'recommendations:': 4, 'assessment and plan:': 10, 'impression ': 3, 'initial assessment:': 1, 'plan:': 4, 'assessment:': 5, 'imp:': 2, 'ass:': 1, 'interpretation:': 1}, 'present_illness': {'history of present illness:': 294, 'history of the present illness:': 5}, 'past_medical_history': {'past medical history:': 349, 'history:': 46, 'past medical history': 35, 'mh': 71, 'mhx': 30, 'medical history': 13, 'pmh:': 20, 'past medical hx': 1, 'past medical': 2}, 'patient_instructions': {'discharge instructions:': 78}, 'family_history': {'family history:': 152}, 'labs_and_studies': {'laboratory data:': 28, 'labs:': 44, 'micro:': 8, 'indication:': 6, 'pathology report:': 1}, 'allergy': {'allergies:': 65, 'allergy': 4, 'sensitivities:': 5}, None: {None: 12}, 'other': {'note:': 6, 'sp:': 10, 'procedure:': 2}, 'hiv_screening': {'hiv:': 2}, 'medication': {'discharge medications:': 1, 'medications on discharge:': 1, 'medications:': 1}, 'problem_list': {'problem list': 1}}, 'echo': {'labs_and_studies': {'indication:': 2}}, 'nursing': {'observation_and_plan': {'assessment:': 396, 'plan:': 413, 'a/p:': 1}, 'past_medical_history': {'mh': 141, 'history:': 81, 'pmh:': 80, 'mhx': 38, 'past medical history:': 11, 'past medical history': 17, 'clinical history:': 3}, None: {None: 743}, 'sexual_and_social_history': {'social history:': 13}, 'medication': {'drugs:': 4, 'meds:': 8}, 'other': {'sp:': 6, 'note:': 7}, 'labs_and_studies': {'labs:': 1}, 'present_illness': {'history of present illness:': 3, 'present illness:': 1}}, 'physician ': {'sexual_and_social_history': {'social history:': 222, 'sh:': 10}, 'observation_and_plan': {'a:': 115, 'assessment:': 10, 'plan:': 31, 'diagnoses:': 1, 'assessment and plan:': 17, 'impression:': 21, 'a/p:': 7, 'diagnosis:': 2, 'assesment:': 3, 'medical decision making:': 1}, 'labs_and_studies': {'labs:': 405, 'micro:': 14}, None: {None: 277}, 'past_medical_history': {'mhx': 34, 'mh': 76, 'history:': 17, 'medical history': 4, 'pmh:': 11, 'past medical history:': 8, 'past medical': 1, 'past medical history': 23, 'clinical history:': 2}, 'physical_exam': {'review of systems:': 8, 'physical examination': 19}, 'other': {'note:': 11}, 'family_history': {'family history:': 5}, 'medication': {'drugs:': 5, 'current medications:': 2, 'meds:': 1}, 'problem_list': {'problem list': 1}, 'allergy': {'allergies:': 3}}, 'social work': {'observation_and_plan': {'assessment:': 50, 'plan:': 3}, 'past_medical_history': {'history:': 49, 'mh': 2, 'medical hx': 2}, 'other': {'note:': 13}, None: {None: 26}, 'family_history': {'family history:': 5}, 'present_illness': {'history of present illness:': 1}}, 'respiratory ': {'observation_and_plan': {'assessment:': 1}, None: {None: 1}}, 'rehab services': {None: {None: 1}, 'past_medical_history': {'pmh:': 2, 'history:': 4}}, 'nutrition': {'past_medical_history': {'mhx': 8, 'mh': 14, 'pmh:': 1}, 'labs_and_studies': {'labs:': 3}}, 'consult': {'past_medical_history': {'past medical history:': 1}, 'sexual_and_social_history': {'social history:': 2}}, 'general': {None: {None: 10}, 'family_history': {'family history:': 1}, 'medication': {'meds:': 2}}, 'case management ': {'observation_and_plan': {'assessment:': 1}}, 'radiology': {'labs_and_studies': {'indication:': 32, 'clinical indication:': 1}, 'past_medical_history': {'history:': 21, 'clinical history:': 2}, None: {None: 16}, 'other': {'procedure:': 1}, 'observation_and_plan': {'diagnosis:': 119, 'impression ': 2}}, 'nursing/other': {None: {None: 405}, 'other': {'sp:': 79, 'note:': 50}, 'observation_and_plan': {'plan:': 75, 'a:': 32, 'a/p:': 15, 'assessment:': 1, 'impression ': 1}, 'allergy': {'allergy:': 5, 'allergy': 1, 'allergies:': 17}, 'past_medical_history': {'mhx': 13, 'mh': 69, 'pmh:': 38, 'past medical history': 3, 'medical hx': 1, 'medical history': 1}, 'medication': {'meds:': 3}, 'physical_exam': {'review of systems:': 14}, 'labs_and_studies': {'s/o:': 4, 'labs:': 3}, 'sexual_and_social_history': {'sh:': 3}}}
pprint.pprint(section_guidelines)


# In[3]:


section_guidelines.keys()


# In[5]:


(SIDs, HADMIDs) = pkl.load(open('../resources/sids_hadmids.pkl', 'rb'))


# In[6]:


print(SIDs.__len__(), set(SIDs).__len__())
print(HADMIDs.__len__(), set(HADMIDs).__len__())


# In[7]:


with open("../resources/NOTEEVENTS.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    sectionizer = TextSectionizer()

    # based on sections we know contain suicide, extract all sections from notes to create annotation dataset
    # attributes: ROW_ID,  SUBJECT_ID, HADM_ID, CHARTDATE, CHARTTIME, STORETIME, CATEGORY, DESCRIPTION, START_POS, END_POS
    data = []
    counter = 0
    for row in tqdm(reader):
        category = row[6].lower()

        if row[6] == "CATEGORY" or not (category in section_guidelines):
            continue
        if (row[1] == '' or row[2] == ''):
            continue
        if int(row[1]) in SIDs and int(row[2]) in HADMIDs:
            
            sections = sectionizer(row[10])
            extraction = ""
            pos = []
            for section_title, section_header, section_text in sections:
                title =  None if section_title is None else section_title.lower()
                header = None if section_header is None else section_header.lower()
                text = section_text.lower()

                if category in section_guidelines and title in section_guidelines[category] and header in section_guidelines[category][title]:
                    extraction = extraction + "\n\n" + section_text
                    start = row[10].index(section_text)
                    pos.append((start, start + len(section_text)))
                
            # print("Category: ", category)
            # print("Extracted text: ", extraction)
            # print("*****")
            data.append([row[0], row[1], row[2], row[3], row[4], row[6], extraction, pos])

            # print("Original: ", text)
            # print("Verify: ", row[10][start: start + len(text)])
    print("FINISHED EXTRACTING DATA")
    print("Total Files:", data.__len__())


# In[8]:


fields = ["ROW_ID",  "SUBJECT_ID", "HADM_ID", "CHARTDATE", "CHARTTIME", "CATEGORY", "DESCRIPTION", "STARTEND_POSITIONS"]
with open("../resources/tmp_data.csv", "w", newline="") as dataset_csvfile:
    csvwriter = csv.writer(dataset_csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(data)


# In[ ]:


with open("../data/tmp_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile)
    dir = "../corpus/"
    for row in tqdm(reader):
        if 
        file_path = path.join(dir, str(row[1]) + "_" + str(row[2]))
        if not path.exists(file_path):
            f = open(file_path, "w+")
            f.write(row[6])
            f.close()
        else:
            f = open(file_path, "a+")
            f.write(row[6])
            f.close()


# In[9]:


files_new = listdir('../corpus/')


# In[11]:


files_new = [x for x in files_new if 'SUBJECT' not in x]


# In[13]:


print('Total Hospital Admissions:', files_new.__len__())


# In[ ]:





# In[ ]:




