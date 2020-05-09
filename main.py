#!/usr/bin/env python3

"""
This version of the source code was made by improving the original deats program
Should be the most up to date
"""

import json
import os
import sys
import glob
from zfin_ftns import *
from deats_ftns import *

#CLEAR DIRECTORIES/DELETE CERTAIN FILES FOR FRESH START
metadata_f_l = glob.glob('meta_data/*.csv')
data_f_l = glob.glob('data/*.csv')
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
json_file = json.load(open(args.zfin_data,"r"))
zfa_file = open(args.zfa_data, "r")
bspo_file = open(args.bspo_data, "r")
stage_file = open(args.stage_file, "r")
#SET FILTERS
pete_score = int(args.pete_score)
stage_name = args.stage_name
#READ IN DEG DATA AND OPEN A METADATA FILE
m_deg_set = args.multiple_sets
s_deg_set = args.single_set
if m_deg_set != None:
    m_deg_set = open(args.multiple_sets, "r")
else:
    s_deg_set = open(args.single_set, "r")
    metadata_f = open("meta_data/meta_data.csv", "w")
    data_f = open("data/data.csv", "w")
    pete_score = 0
#OPEN ZFIN STATS FILE
term_freq_outf = open("stats/dist.csv","w")

### PARSE ZFIN DATA

# create anatomy_id:anatomy_terms dictionary
terms_ref_d = mk_terms_ref_d(zfa_file, bspo_file) #chkd

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
    dev_stage, ensdarg, anatomy_id, gene_sym = parse_records(record) #chkd
    # create ensdarg:anatomy_term dict for each stage (plus 'all_stages') and create anatomy_term:freq dict
    stage_anat_d, term_freq_d = mkstage_anat_dict(dev_stage, ensdarg, anatomy_id, terms_ref_d, stage_anat_d, term_freq_d) #stage:{ensdarg:term} and #{term:freq} #chkd

    #counter += 1 
##CONFUSING PRINT STATEMENTS
#for stage_name in stage_anat_d:
    #print(stage_name)
    #print(stage_anat_d[stage_name])
    #for j in stage_anat_d[stage_name]:
    #    print(j)
    #    print(stage_anat_d[stage_name][j])
    #sys.exit()

    # create ensdarg:gene_symbol dict
    ensdarg_sym_d = mkensdarg_symbol_dict(ensdarg, gene_sym, gene_sym_d) #{ensdarg:symbol} #check
    counter += 1

# print term freq dict
for anatomy_term in term_freq_d:
    term_freq_outf.write(str(anatomy_term) + "," + str(term_freq_d[anatomy_term]) + "\n")

### PARSE SINGLE DEGS TEXT
if s_deg_set != None:
    # create deg list
    sing_deg_l = mkdeg_list(s_deg_set) #[ensdarg,ensdarg]
    # print metadata
    for ensdarg in sing_deg_l:
        if ensdarg in ensdarg_sym_d:
            metadata_f.write(ensdarg + "\t" + "\t".join(ensdarg_sym_d[ensdarg]) + "\n")
        else:
            metadata_f.write(ensdarg + "\t" + "unknown" + "\n")
    # use the parsed zfin data to convert deg to anatomy terms
    uncounted_deat_l = ensdarg_to_term_deg(sing_deg_l, stage_anat_d[stage_name]) #[term,term]
    # create an anatomy terms:count dict for each cluster
    deat_d = terms_counter_deg(uncounted_deat_l) #{term:freq}
    # print out deats
    for term in deat_d:
        data_f.write(str(term) + "," + str(deat_d[term]) + "\n")

### PARSE MULTI DEGS FILE
else:
    # create cluster:degs dict, deats_fp dict, and metadata_fp dict
    m_deg_d, data_fp_d, metadata_fp_d = mkdegs_dict(m_deg_set) #{cluster:(ensdarg,pete_score)}
    # filter the degs by pete_score
    filtered_degs_d = filter_degs(m_deg_d, pete_score) #{cluster:[ensdarg,ensdarg]}
    # print metadata
    for cluster in filtered_degs_d:
        for ensdarg in filtered_degs_d[cluster]:
            if ensdarg in ensdarg_sym_d:
                metadata_fp_d[cluster].write(ensdarg + "\t" + "\t".join(ensdarg_sym_d[ensdarg]) + "\n")
            else:
                metadata_fp_d[cluster].write(ensdarg + "\t" + "unknown" + "\n")
    # use the parsed zfin data (stage_anat_d) to convert degs to anatomy terms
    uncounted_deat_d = ensdarg_to_term_degs(filtered_degs_d, stage_anat_d[stage_name]) #{cluster:[term,term]}
    # create an anatomy terms:count dict for each cluster
    deat_d = terms_counter_degs(uncounted_deat_d) #{cluster:{term:freq}}
    #print out deats
    for cluster in deat_d:
        for term in deat_d[cluster]:
            data_fp_d[cluster].write(str(term) + "," + str(deat_d[cluster][term]) + "\n")

"""
Example Single DEG Set Command
./main.py \
-zfin_data files/zfin_wt_expression.json \
-single_set files/sdeg_set.tsv \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt \
-stage_str all_stages
"""
"""
Example Multi DEG Set Command
./main.py \
-zfin_data files/zfin_wt_expression.json \
-multiple_sets mdeg_set.tsv \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt \
-pete_score 16 \
-stage_str all_stages
"""
