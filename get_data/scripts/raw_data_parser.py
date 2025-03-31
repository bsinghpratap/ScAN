import re, os
import csv
import sys
from pprint import pprint
import pandas as pd
import pickle as pkl
from os.path import join, isdir
from os import listdir, path
from tqdm import tqdm
import json
from clinical_sectionizer import TextSectionizer


class dataExtractor():
    """Extract the notes for each of the patient and collate them together."""
    def __init__(self, guidelines_addr="../resources/section_guidelines.json", 
                 notevents_addr="../resources/NOTEEVENTS.csv", 
                 sids_hadmids_addr="../resources/sids_hadmids.pkl"):
        self.section_guidelines = json.load(open(guidelines_addr, 'r'))
        self.notevents_addr = notevents_addr
        self.sids_hadmids_addr = sids_hadmids_addr

    def read_data(self):
        (SIDs, HADMIDs) = pkl.load(open(self.sids_hadmids_addr, 'rb'))
        with open(self.notevents_addr, newline="") as csvfile:
            reader = csv.reader(csvfile)
            sectionizer = TextSectionizer()
            # extracting sections that may contain suicide-related information
            # attributes: ROW_ID,  SUBJECT_ID, HADM_ID, CHARTDATE, CHARTTIME, STORETIME, CATEGORY, DESCRIPTION, START_POS, END_POS
            data = []
            counter = 0
            for row in reader:
                category = row[6].lower()
                if category not in self.section_guidelines:
                    continue
                if (row[1] == '' or row[2] == ''):
                    continue
                if int(row[1]) in SIDs and int(row[2]) in HADMIDs:
                    sections = sectionizer(row[10])
                    extracted_text = ""
                    pos = []
                    for section_title, section_header, section_text in sections:
                        title =  None if section_title is None else section_title.lower()
                        header = None if section_header is None else section_header.lower()
                        text = section_text.lower()
        
                        if category in self.section_guidelines and title in self.section_guidelines[category] and header in self.section_guidelines[category][title]:
                            extracted_text += "\n\n" + section_text
                            start = row[10].index(section_text)
                            pos.append((start, start + len(section_text)))
                    data.append([row[0], row[1], row[2], row[3], row[4], row[6], extracted_text, pos])
            print(f'Total Files: len(data)')
        return data

    def create_corpus(self, data, corpus_dir):
        if not isdir(corpus_dir):
            os.mkdir(corpus_dir)
        for row in tqdm(data):
            file_path = path.join(corpus_dir, str(row[1]) + "_" + str(row[2]))
            if not path.exists(file_path):
                f = open(file_path, "w+")
                f.write(row[6])
                f.close()
            else:
                f = open(file_path, "a+")
                f.write(row[6])
                f.close()

