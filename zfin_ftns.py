#!/usr/bin/env python3

"""
Notes:
1. whereExpressed in database json is more detailed than zfa/bspo ids
2. for mkdegs_dict what is happening if pct2 = 0?
3. if terms appears twice for same ensdarg and stage it should not be counted twice...what is the context
   of this question for "all_stages"?
"""
import argparse
import sys

def get_args():
    parser = argparse.ArgumentParser(description="a tool help researchers identify the cell types in zebrafish")
    parser.add_argument("-single_set", "--single_set", help="differentially expressed genes in an cell of unknown type", required=False, type = str)
    parser.add_argument("-multiple_sets", "--multiple_sets", help="sets of differentially expressed genes generated from a library of cells of unknown types", required=False, type = str)
    parser.add_argument("-zfin_data", "--zfin_data", help="json file with zfin data", required=True, type = str)
    parser.add_argument("-zfa", "--zfa_data", help="", required=True, type = str)
    parser.add_argument("-bspo", "--bspo_data", help="", required=True, type = str)
    parser.add_argument("-stage_file", "--stage_file", help="", required=True, type = str)
    parser.add_argument("-pete_score", "--pete_score", help="", required=False, type = int, default=0)
    parser.add_argument("-stage_str", "--stage_name", help="", required=False, type = str, default='all stages')
    return parser.parse_args()

def mk_terms_ref_d(zfa_file, bspo_file):
    "takes in zID:zANAT database files and returns a clean dictionary organizing zID:zANAT into a key:value pair"
    ref_dict = {}
    for line in zfa_file:
        line=line.strip().split()
        for item in line[:]:
            if "ZDB-STAGE" in item:
                line.remove(item)
        line[1:] = [' '.join(line[1:])]
        ref_dict[line[0]] = line[1] #{'ZFA:0001249': exocrine pancreas}
    for line in bspo_file:
        line=line.strip().split()
        line[1:] = [' '.join(line[1:])]
        ref_dict[line[0]] = line[1]  #{'BSPO:0004229':'corneal endothelium'}
    return ref_dict

def parse_records(record):
    "save all relevant information in the JSON file to variables"
    anatomy_id = []
    ensdarg = None
    for item in record:
        if item == "ensemblCrossReferences":
            if record[item] != []:
                ensdarg = record[item][0]["id"]
                ensdarg = ensdarg.split(":")[1]
        if item == "geneSymbol":
            gene_symbol = record[item]
        if item =="geneName":
            gene_name = record[item]
        if item == "whenExpressed":
            dev_stage = record[item]["stageName"]
        if item == "whereExpressed":
            super_structure_info = record[item]
            anatomy_id = []
            if "anatomicalStructureTermId" in super_structure_info:
                if super_structure_info["anatomicalStructureTermId"] != 'ZFA:0001093':
                    if super_structure_info["anatomicalStructureTermId"] != 'ZFA:0001094':
                        anatomy_id.append(super_structure_info["anatomicalStructureTermId"])
            if "anatomicalSubStructureTermId" in super_structure_info:
                anatomy_id.append(super_structure_info["anatomicalSubStructureTermId"])
            if "anatomicalStructureQualifierTermId" in super_structure_info:
                anatomy_id.append(super_structure_info["anatomicalStructureQualifierTermId"])
    return dev_stage, ensdarg, anatomy_id, gene_symbol

def mkstage_anat_dict(dev_stage, ensdarg, anatomy_id, terms_ref_d, stage_anat_d, term_freq_d):
    """
    creates two dictionaries. the first contains a dictionary for each dev stage where the ensdargs associated with that dev stage are the keys
    and the anat_terms are the values. also included in this dictionary is an 'all_stages' dictionary which has all the endargs as keys and all
    the anat_terms. the second dictionary tallies the frequency of all the anat_terms in the JSON file.
    """
    if anatomy_id != []:
        anatomy_terms = []
        #convert id to terms
        for id in anatomy_id:
            if id in terms_ref_d.keys():
                anatomy_terms.append(terms_ref_d[id])
        #initialize all_stages dict
        if 'all_stages' not in stage_anat_d.keys():
            stage_anat_d['all_stages'] = {}
        #have consistent char for delim
        dev_stage = dev_stage.replace(" ","_").replace(":","_") 
        #make ensdarg:term per dev_stage
        if dev_stage not in stage_anat_d:
            stage_anat_d[dev_stage] = {}
            stage_anat_d[dev_stage][ensdarg] = anatomy_terms
        else: #dev_stage is in stage_anat_d
            if ensdarg not in stage_anat_d[dev_stage]:
                stage_anat_d[dev_stage][ensdarg] = anatomy_terms
            else:
                for term in anatomy_terms:
                    if term not in stage_anat_d[dev_stage][ensdarg]: #for repeat ensdargs do not add repeat terms
                        stage_anat_d[dev_stage][ensdarg].append(term)
        #make all stages dict
        if ensdarg not in stage_anat_d['all_stages']:
            stage_anat_d['all_stages'][ensdarg] = anatomy_terms 
        else:
            for term in anatomy_terms:
                if term not in stage_anat_d['all_stages'][ensdarg]: #for repeat ensdargs does not add repeat anat terms
                    stage_anat_d['all_stages'][ensdarg].append(term)
        #make freq dict
        for term in anatomy_terms:
            if term not in term_freq_d:
                term_freq_d[term] = 1
            else:
                term_freq_d[term] += 1
    return stage_anat_d, term_freq_d

def mkensdarg_symbol_dict(ensdarg, gene_symbol, global_dict):
    "make a list with the ensdarg as the key and (list of) gene symbols as value"
    if ensdarg not in global_dict:
        global_dict[ensdarg] = []
        global_dict[ensdarg].append(gene_symbol)
    else:
        if gene_symbol not in global_dict[ensdarg]:
            global_dict[ensdarg].append(gene_symbol)
    return global_dict #{'ENSDARG00000021184': ['rbfox1l']}

## PARSE DEGS
#def mkdegs_dict(file):
#    cluster_d = {}
#    cluster_fp_d = {}
#    metadata_fp_d = {}
#    for line in file:
#        if "p_val" not in line:
#            list=line.strip().split() #list[6] is cluster list[7] is ENSDARG list[8] p1/p2*lf score

#            if float(list[4]) == 0:
#                float(list[4]) == 1e-10
#            list.append((float(list[3])/float(list[4]))*float(list[2])) #pct1/pct2*lfc
#            tup = (list[7],list[8])
#            if (str(int(list[6])+1)) not in cluster_d:
#                cluster_d[str(int(list[6])+1)] = []
#                cluster_d[str(int(list[6])+1)].append(tup)
#            else:
#                cluster_d[str(int(list[6])+1)].append(tup)

##            if float(list[4]) != 0:
##                list.append((float(list[3])/float(list[4]))*float(list[2])) #pct1/pct2*lfc
##                tup = (list[7],list[8])
##                if (str(int(list[6])+1)) not in cluster_d:
##                    cluster_d[str(int(list[6])+1)] = []
##                    cluster_d[str(int(list[6])+1)].append(tup)
##                else:
##                    cluster_d[str(int(list[6])+1)].append(tup)

#            cluster_fp = open("data/{0}.csv".format(str(int(list[6])+1)),"w") #Add one to start cluster count at 1
#            cluster_fp_d[str(int(list[6])+1)] = cluster_fp
#            metadata_fp = open("meta_data/{0}.csv".format(str(int(list[6])+1)),"w")
#            metadata_fp_d[str(int(list[6])+1)] = metadata_fp
#    return cluster_d, cluster_fp_d, metadata_fp_d

#def mkdeg_list(file):
#    sing_deg_l = []
#    for line in file:
#        line = line.strip()
#        sing_deg_l.append(line)
#    return sing_deg_l

#def filter_degs(multi_degs_d, pete_score):
#    ensdarg_sorted_l = []
#    #sort tups
#    for cluster in multi_degs_d:
#        ensdarg_tup_l = multi_degs_d[cluster]
#        ensdarg_tup_l.sort(key = lambda x: x[1], reverse=True)
#        multi_degs_d[cluster] = ensdarg_tup_l
#    #discard pete_scores
#    for cluster in multi_degs_d:
#        ensdarg_l = []
#        for tup in multi_degs_d[cluster]:
#            ensdarg_l.append(tup[0])
#            multi_degs_d[cluster] = ensdarg_l
#    for cluster in multi_degs_d:
#        list_length = len(multi_degs_d[cluster])
#        if list_length <= pete_score:
#            multi_degs_d[cluster] = multi_degs_d[cluster]
#        else:
#            multi_degs_d[cluster] = multi_degs_d[cluster][:pete_score]
#    return multi_degs_d

#def ensdarg_to_term_degs(filtered_degs_d, zfin_anatomy_d):
#    for cluster in filtered_degs_d: #{1:[ensdarg,ensdarg]}
#        anat_terms_l = []
#        for ensdarg in filtered_degs_d[cluster]:
#            if ensdarg in zfin_anatomy_d:
#                for anat_term in zfin_anatomy_d[ensdarg]:
#                    anat_terms_l.append(anat_term)
#                filtered_degs_d[cluster] = anat_terms_l
#    return filtered_degs_d

#def ensdarg_to_term_deg(sing_deg_l, zfin_anatomy_d):
#    anat_terms_l = []
#    for ensdarg in sing_deg_l:
#        if ensdarg in zfin_anatomy_d:
#            for anat_term in zfin_anatomy_d[ensdarg]:
#                anat_terms_l.append(anat_term)
#    return anat_terms_l

#def terms_counter_degs(uncounted_deat_d):
#    """counts the number of unique term in a dictionary"""
#    for cluster in uncounted_deat_d:
#        term_counts_dict = {}
#        for term in uncounted_deat_d[cluster]:
#            if term not in term_counts_dict:
#                term_counts_dict[term] = 1
#            else:
#                term_counts_dict[term] += 1
#        uncounted_deat_d[cluster] = term_counts_dict
#    return uncounted_deat_d

#def terms_counter_deg(uncounted_deat_l):
#    term_counts_dict = {}
#    for term in uncounted_deat_l:
#        if term not in term_counts_dict:
#            term_counts_dict[term] = 1
#        else:
#            term_counts_dict[term] += 1
#    return term_counts_dict
