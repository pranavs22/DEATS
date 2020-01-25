#!/usr/bin/env python3

import argparse
import json
import os
import glob
from main_ftns import *


def get_args():
    parser = argparse.ArgumentParser(description="ZFIN cell annotater")
    parser.add_argument("-zfin", "--zfin", help="ZFIN's JSON FILE", required=True, type = str)
    parser.add_argument("-multiple_lists", "--multiple_lists", help="List of Differentially Expressed Genes per Cell-Type", required=False, type = str)
    parser.add_argument("-single_list", "--single_list", help="List of Differentially Expressed Genes", required=False, type = str)
    parser.add_argument("-zfa", "--zfa_data", help="use to specify the amount of epochs", required=True, type = str)
    parser.add_argument("-bspo", "--bspo_data", help="use to specify the batch size", required=True, type = str)
    parser.add_argument("-stage_file", "--stage_file", help="use to specify the number of dense layers", required=True, type = str)
    parser.add_argument("-pete", "--pete_filt", help="use to specify the number of dense layers", required=False, type = int, default=0)
    parser.add_argument("-stage", "--specimen_stages", help="use to specify the number of dense layers", required=False, type = str, default='all stages')
    return parser.parse_args()

args = get_args()

#CLEAR DIRECTORIES FOR FRESH START
meta_data_files_list = glob.glob('meta_data/*.tsv')
data_files_list = glob.glob('data/*.tsv')
try:
    os.remove("files/biomarkers.tsv")
except IOError:
    pass
try:
    for meta_data_file in meta_data_files_list:
        os.remove(meta_data_file)
except IOError:
    pass
try:
    for data_files in data_files_list:
        os.remove(data_files)
except IOError:
    pass

#ZFIN DATA
JSON_FILE = open(args.zfin, "r")
json = json.load(JSON_FILE)
ZFA_TABLE =  open(args.zfa_data, "r")
BSPO_TABLE =  open(args.bspo_data, "r")
STAGE_NAME_FILE = open(args.stage_file, "r")

#ZFIN STATS FILE
ZFIN_ANAT_TERMS_DIST = open("stats/dist.tsv","w")

#FILTERS
PETE_FILT = int(args.pete_filt)
STAGE = args.specimen_stages

#DEG DATA
DEG_LISTS = args.multiple_lists
DEG_LIST = args.single_list
if DEG_LISTS != None:
    DEG_LISTS = open(args.multiple_lists, "r")
elif DEG_LIST != None:
    DEG_LIST = open(args.single_list, "r")
    REFERENCE_FILE = open("meta_data/meta_data.tsv", "w")
    OUTPUT_FILE = open("data/data.tsv", "w")
    PETE_FILT = 0
else:
    print("***ERROR***" + "\n" + "Sorry, this program does NOT work for if BOTH Single and Multiple DEG Lists are uploaded.")
    exit()

###PREP ZFIN DATA
print("Starting")

# CREATE DICTIONARY: KEYS=STAGE_NAMES & VALUES=BLANK DICTIONARIES
STAGE_NAMES_DICT = {}
for stage_name in STAGE_NAME_FILE:
    stage_name = stage_name.strip()
    # if ":" in stage_name: #replace ":" with "_" for consistent character to replace with space later
    #     stage_name.replace(":","_")
    STAGE_NAMES_DICT[stage_name] = {}

# CREATE:
    #1)ENSDARG ANATOMY_ID DICTIONARY "ENSDARG_ANATOMY_ID_DICT" #{'ENSDARG00000021184': ['ZFA:0000003', 'ZFA:0003022']}
    #2) ENSDARGS GENE_SYMBOL DICTIONARY "ENSDARGS_GENE_SYMBOL_DICT" #{'ENSDARG00000021184': ['rbfox1l']}
    #3) STAGE_NAMES ENSDARGS ANATOMY_ID DICTIONARY
ENSDARG_ANATOMY_ID_DICT = {}

ENSDARGS_GENE_SYMBOL_DICT = {}
counter = 0

while(True):
    try:
        record = json["data"][counter]
    except IndexError:
        break
    ensdarg, gene_symbol, gene_name, dev_stage, anatomy_id = parse_records(record)
    counter += 1

    #MAKE A DICTIONARY OF ENSDARGS AND GENE_SYMBOLS
    if ensdarg not in ENSDARGS_GENE_SYMBOL_DICT:
        ENSDARGS_GENE_SYMBOL_DICT[ensdarg] = []
        ENSDARGS_GENE_SYMBOL_DICT[ensdarg].append(gene_symbol)
    else:
        if gene_symbol not in ENSDARGS_GENE_SYMBOL_DICT[ensdarg]:
            ENSDARGS_GENE_SYMBOL_DICT[ensdarg].append(gene_symbol)

    #MAKE DICTIONARIES OF ENSDARGS AND ANATOMY_IDS
    if ensdarg not in ENSDARG_ANATOMY_ID_DICT:
        ENSDARG_ANATOMY_ID_DICT[ensdarg] = anatomy_id
    else:
        for id in anatomy_id:
            if id not in ENSDARG_ANATOMY_ID_DICT[ensdarg]:
                ENSDARG_ANATOMY_ID_DICT[ensdarg].append(id)

    #MAKE DICTIONARY FOR IDS OF SPECIFIC DEV STAGES
    if dev_stage in STAGE_NAMES_DICT:
        if ensdarg not in STAGE_NAMES_DICT[dev_stage]:
            STAGE_NAMES_DICT[dev_stage][ensdarg] = anatomy_id
        else:
            for id in anatomy_id:
                if id not in STAGE_NAMES_DICT[dev_stage][ensdarg]:
                    STAGE_NAMES_DICT[dev_stage][ensdarg].append(id)
    #ADD ALL STAGES KEY/VALUE
    STAGE_NAMES_DICT['all_stages'] = ENSDARG_ANATOMY_ID_DICT #ADD GENERAL DICTIONARY TO DICTIONARY WITH SPECIFIC DEV STAGES

#RENAME DEV STAGE DICTIONARY FOR CLARITY
STAGE_NAMES_DICT_RENAME = {}
for stage_name in STAGE_NAMES_DICT:
    if " " or ":" in stage_name:
        new_stage_name = stage_name.replace(" ","_").replace(":","_")
        STAGE_NAMES_DICT_RENAME[new_stage_name] = STAGE_NAMES_DICT[stage_name]
    else:
        STAGE_NAMES_DICT_RENAME[stage_name] = STAGE_NAMES_DICT[stage_name]

#CONFUSING PRINT STATEMENTS
# for stage_name in STAGE_NAMES_DICT_RENAME:
#     print(stage_name)
#     print(STAGE_NAMES_DICT_RENAME[stage_name])
#     for j in STAGE_NAMES_DICT_RENAME[stage_name]:
#         print(j)
#         print(STAGE_NAMES_DICT_RENAME[stage_name][j])

# CREATE DICTIONARY: KEY=ZFA & VALUE=ANATOMY TERM
ZFA_DICT = {}
for line in ZFA_TABLE:
    line=line.strip().split()
    for item in line[:]:
        if "ZDB-STAGE" in item:
            line.remove(item)
    line[1:] = [' '.join(line[1:])]
    ZFA_DICT[line[0]] = line[1] #{'ZFA:0001249': exocrine pancreas}"""

# CREATE DICTIONARY: KEYS=BSPO & VALUE=ANATOMY TERM
BSPO_DICT = {}
for line in BSPO_TABLE:
    line=line.strip().split()
    line[1:] = [' '.join(line[1:])]
    BSPO_DICT[line[0]] = line[1]  #{'BSPO:0004229':'corneal endothelium'}"""

# FOR STATISTICAL ANALYSIS CREATE A LIST OF ALL ANATOMY TERMS IN ZFIN
ANATOMY_TERMS_LIST = []
for ensdarg in ENSDARG_ANATOMY_ID_DICT: #{'ENSDARG00000021184': ['ZFA:0000003', 'ZFA:0003022']}
    for anatomy_term in convert_id_to_terms(ENSDARG_ANATOMY_ID_DICT[ensdarg],ZFA_DICT, BSPO_DICT):
        ANATOMY_TERMS_LIST.append(anatomy_term)
#count the frequency of those terms
contin_dict = terms_counter(ANATOMY_TERMS_LIST)
#print out to a file
for anatomy_term in contin_dict:
    ZFIN_ANAT_TERMS_DIST.write(str(anatomy_term) + "," + str(contin_dict[anatomy_term]) + "\n")

###############################################################################################################################################
    """
    PREP MULTIPLE DEGs FILE
    """
print("Half Way")
if DEG_LISTS != None:
    # CREATE A DICTIONARY: KEYS=CELL-TYPE & VALUE=LIST OF TUPLES (ENSDARGS & P1/P2*LFC) #{"0":[('ENSDARG00000037821', 0.33405981),('ENSDARG00000037514', 0.8290391),('ENSDARG00000037993', 0.9289919)]}
    CLUSTER_DICT = {}
    CLUSTER_FP_DICT = {}
    META_DATA_DICT = {}
    for line in DEG_LISTS:
        if "p_val" not in line:
            list=line.strip().split() #list[6] is cluster list[7] is ENSDARG list[8] p1/p2*lf score
            if float(list[4]) != 0:
                list.append((float(list[3])/float(list[4]))*float(list[2])) #pct1/pct2*lfc
                tup = (list[7],list[8])
                CLUSTER_FP = open("data/{0}.tsv".format(str(int(list[6])+1)),"w") #Add one to start cluster count at 1
                CLUSTER_FP_DICT[str(int(list[6])+1)] = CLUSTER_FP
                META_DATA_FP = open("meta_data/{0}.tsv".format(str(int(list[6])+1)),"w")
                META_DATA_DICT[str(int(list[6])+1)] = META_DATA_FP
                if (str(int(list[6])+1)) not in CLUSTER_DICT:
                    CLUSTER_DICT[str(int(list[6])+1)] = []
                    CLUSTER_DICT[str(int(list[6])+1)].append(tup)
                else:
                    CLUSTER_DICT[str(int(list[6])+1)].append(tup)

    # SORT THE LIST OF TUPLES BY P1/P2*LFC SCORES FOR DOWNSTREAM FILTERING
    for cluster in CLUSTER_DICT:
        sorted_ensdargs_with_tup = sort_tuple_list_by_second_item(CLUSTER_DICT[cluster])
        CLUSTER_DICT[cluster] = sorted_ensdargs_with_tup #{"0":[('ENSDARG00000037993', 0.9289919),('ENSDARG00000037514', 0.8290391), ('ENSDARG00000037821', 0.33405981)]}

    # FOR EACH CLUSTER TALES ENSDARG OUT OF TUPLE
    for cluster in CLUSTER_DICT:
        filtered_ensdarg_lst = flatten_sorted_list(CLUSTER_DICT[cluster])
        CLUSTER_DICT[cluster] = filtered_ensdarg_lst #{"0":['ENSDARG00000037993','ENSDARG00000037514', 'ENSDARG00000037821']}"""

    #FOR EACH CLUSTER TAKES THE TOP N NUMBER OF ENSDARGS IN THE LIST
    if PETE_FILT > 0: #default setting PETE_NUM=0
        for cluster in CLUSTER_DICT:
            sorted_ensdarg_lst = top_items_or_less(CLUSTER_DICT[cluster], PETE_FILT) #PETE NUMBER IS ARGPARSED
            CLUSTER_DICT[cluster] = sorted_ensdarg_lst #{"0":['ENSDARG00000037993','ENSDARG00000037514']} EX: TOP 2

    #WRITE OUT DICTIONARY: KEYS=CELL-TYPE & VALUES=ENSDARG LIST
    for cluster in CLUSTER_DICT:
        for ensdarg in CLUSTER_DICT[cluster]:
            if ensdarg in ENSDARGS_GENE_SYMBOL_DICT:
                gene_sym_lst = ENSDARGS_GENE_SYMBOL_DICT[ensdarg]
                gene_sym = "\t".join(gene_sym_lst)
            else:
                gene_sym = "unknown"
            META_DATA_DICT[cluster].write(ensdarg + "\t" + gene_sym + "\n") #0	ENSDARG00000002403

    """
    CREATE DEATS (MERGE DEGs WITH ZFIN DATA)
    """

    #CREATE LIST OF ANATOMY IDS
    for cluster in CLUSTER_DICT:
        zfa_lst = convert_ensdarg_list_to_anatomy_id_list(CLUSTER_DICT[cluster], STAGE_NAMES_DICT_RENAME[STAGE]) #CAN SPECIFY THE STAGE DICTIONARY USED
        CLUSTER_DICT[cluster]=zfa_lst #{'0': ['ZFA:0000050', 'ZFA:0000050', 'ZFA:0000064', 'ZFA:0000050', 'ZFA:0000112', 'ZFA:0001094', 'ZFA:0000056', 'ZFA:0001094']}

    #CONVERT ANATOMY IDS TO ANATOMY TERMS
    for cluster in CLUSTER_DICT:
        zfa_terms_lst = convert_id_to_terms(CLUSTER_DICT[cluster], ZFA_DICT, BSPO_DICT)
        CLUSTER_DICT[cluster]=zfa_terms_lst  #{'0': ['exocrine pancreas', 'heart rudiment', 'swim bladder', 'pronephric duct', 'heart tube', 'cardiovascular system']}"""

    #GET COUNT OF ANATOMY TERMS
    for cluster in CLUSTER_DICT:
        terms_count_dict = terms_counter(CLUSTER_DICT[cluster])
        CLUSTER_DICT[cluster]=terms_count_dict #{'0': {'optic vesicle': 4, 'presumptive retinal pigmented epithelium': 1, 'retina': 4, 'retinal pigmented epithelium': 1}}"""

    #SORTS THE DICT INTO TUPLES
    for cluster in CLUSTER_DICT:
        cluster_dict = sort_id_counts_dict(CLUSTER_DICT[cluster])
        CLUSTER_DICT[cluster]=cluster_dict #{'0': [('whole organism', 21), ('optic vesicle', 4), ('retina', 4), ('eye', 3), ('liver', 2), ('melanocyte', 2)]}"""

    # WRITE DEATS OUT TO FILES
    for cluster in CLUSTER_DICT:
        # print(cluster)
        # if CLUSTER_DICT[cluster] == []:
        #     CLUSTER_FP_DICT[cluster].write("***NOTE*** ZFIN shows no anatomy terms associated with this cell-type's differentially expressed genes")
        for item in CLUSTER_DICT[cluster]:
            # print(item)
            CLUSTER_FP_DICT[cluster].write(str(item[0]) + "," + str(item[1]) + "\n")

    """
    PROCESS SINGLE DEG LIST
    """
else:
    DEG = []
    for line in DEG_LIST:
        list=line.strip().split()
        DEG.append(list[0])
    zfa_lst = convert_ensdarg_list_to_anatomy_id_list(DEG, STAGE_NAMES_DICT_RENAME[STAGE])
    zfa_terms_lst = convert_id_to_terms(zfa_lst, ZFA_DICT, BSPO_DICT)
    terms_count_dict = terms_counter(zfa_terms_lst)
    cluster_dict = sort_id_counts_dict(terms_count_dict)

    # WRITE DEATS OUT TO FILES
    for ensdarg in DEG:
        if ensdarg in ENSDARGS_GENE_SYMBOL_DICT:
            for symbol in ENSDARGS_GENE_SYMBOL_DICT[ensdarg]:
                REFERENCE_FILE.write(ensdarg + "\t" + symbol + "\n") #0	ENSDARG00000002403
    for item in cluster_dict:
        # OUTPUT_FILE.write(str(item[0]) + "\t" + str(item[1]) + "\n")
        OUTPUT_FILE.write(str(item[0]) + "," + str(item[1]) + "\n")


print("End")
JSON_FILE.close()
ZFA_TABLE.close()
BSPO_TABLE.close()

"""
NOTES:
'whole organism polysome' is not counted
"""
