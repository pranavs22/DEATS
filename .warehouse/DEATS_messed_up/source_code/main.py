#!/usr/bin/env python3

"""
This version of the source code was made by improving the original deats program
Should be the most up to date
"""

import json
import os
import glob
from main_ftns import *

#CLEAR DIRECTORIES/DELETE CERTAIN FILES FOR FRESH START
metadata_f_l = glob.glob('meta_data/*.tsv')
data_f_l = glob.glob('data/*.tsv')
try:
    os.remove("files/biomarkers.tsv")
except IOError:
    pass
try:
    for metadata_f in metadata_f_l:
        os.remove(metadata_f)
except IOError:
    pass
try:
    for data_f in data_f_l:
        os.remove(data_f)
except IOError:
    pass
#INITIALIZE ARGSPARSE OBJECT
args = get_args()
#READ IN ZFIN DATA
json_file = json.load(open(args.zfin,"r"))
stages_file = open(args.stage_file, "r")
bspo_file = open(args.bspo_data, "r")
zfa_file = open(args.zfa_data, "r")
#SET FILTERS
pete_score = int(args.pete_filt)
stage = args.specimen_stages
#READ IN DEG DATA AND OPEN A METADATA FILE
degs_file = args.multiple_lists
deg_file = args.single_list
if degs_file != None:
    degs_file = open(args.multiple_lists, "r")
else:
    deg_file = open(args.single_list, "r")
    metadata_f = open("meta_data/meta_data.tsv", "w")
    data_f = open("data/data.tsv", "w")
    pete_score = 0
#OPEN ZFIN STATS FILE
term_freq_outf = open("stats/dist.tsv","w")

### PARSE ZFIN DATA

# create anatomy_id:anatomy_terms dictionary
terms_ref_d = mk_terms_ref_d(zfa_file, bspo_file) #check

stage_anat_d = {} #ensdarg:term dictionary for each stage
gene_sym_d = {} #ensdarg:gene symbols dictionary
term_freq_d = {} #term:frequency dictionary
counter = 0
while 1 == 1:
    try:
        record = json_file["data"][counter]
    except IndexError:
        break
    # parse each record into its components
    dev_stage, ensdarg, anatomy_id, gene_sym = parse_records(record) #check
    # create ensdarg:anatomy_term dict for each stage (plus 'all_stages') and create anatomy_term:freq dict
    stage_anat_d, term_freq_d = mkstage_anat_dict(dev_stage, ensdarg, anatomy_id, terms_ref_d, global_dict_1=stage_anat_d, global_dict_2=term_freq_d) #stage:{ensdarg:term} and #{term:freq} #check
    # create ensdarg:gene_symbol dict
    ensdarg_sym_d = mkensdarg_symbol_dict(ensdarg, gene_sym, gene_sym_d) #{ensdarg:symbol} #check
    counter += 1
# print term freq dict
for anatomy_term in term_freq_d:
    term_freq_outf.write(str(anatomy_term) + "," + str(term_freq_d[anatomy_term]) + "\n")

### PARSE MULTI DEGS FILE
if degs_file != None:
    # create cluster:degs dict, deats_fp dict, and metadata_fp dict
    multi_degs_d, deats_fp_d, metadata_fp_d = mkdegs_dict(degs_file) #{cluster:(ensdarg,pete_score)}
    # filter the degs by pete_score
    filtered_degs_d = filter_degs(multi_degs_d, pete_score) #{cluster:[ensdarg,ensdarg]}
    # print metadata
    for cluster in filtered_degs_d:
        for ensdarg in filtered_degs_d[cluster]:
            if ensdarg in ensdarg_sym_d:
                metadata_fp_d[cluster].write(ensdarg + "\t" + "\t".join(ensdarg_sym_d[ensdarg]) + "\n")
            else:
                metadata_fp_d[cluster].write(ensdarg + "\t" + "unknown" + "\n")
    # use the parsed zfin data (stage_anat_d) to convert degs to anatomy terms
    uncounted_deat_d = ensdarg_to_term_degs(filtered_degs_d, stage_anat_d[stage]) #{cluster:[term,term]}
    # create an anatomy terms:count dict for each cluster
    deat_d = terms_counter_degs(uncounted_deat_d) #{cluster:{term:freq}}
    #print out deats
    for cluster in deat_d:
        for term in deat_d[cluster]:
            deats_fp_d[cluster].write(str(term) + "," + str(deat_d[cluster][term]) + "\n")

### PARSE SINGLE DEGS TEXT
else:
    # create deg list
    sing_deg_l = mkdeg_list(deg_file)
    # print metadata
    for ensdarg in sing_deg_l:
        if ensdarg in ensdarg_sym_d:
            metadata_f.write(ensdarg + "\t" + "\t".join(ensdarg_sym_d[ensdarg]) + "\n")
        else:
            metadata_f.write(ensdarg + "\t" + "unknown" + "\n")
    # use the parsed zfin data to convert deg to anatomy terms
    uncounted_deat_d = ensdarg_to_term_deg(sing_deg_l, stage_anat_d[stage]) #{cluster:[term,term]}
    # create an anatomy terms:count dict for each cluster
    deat_d = terms_counter_deg(uncounted_deat_d) #{cluster:{term:freq}}
    # print out deats
    for term in deat_d:
        data_f.write(str(term) + "," + str(deat_d[term]) + "\n")

"""
Example Single Command
./json_parser.py \
-zfin files/zfin_wt_expression.json \
-single_list files/deg.tsv \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt \
-stage all_stages
"""
"""
Example Multi Command
./json_parser.py \
-zfin files/zfin_wt_expression.json \
-multiple_lists ../../bgmp_proj_shared/Test_Files/test.tsv \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt \
-pete 16 \
-stage all_stages
"""
