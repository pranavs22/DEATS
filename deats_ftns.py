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


# Single DEG Functions
def mkdeg_list(file):
    """create list of DEG in set"""
    sing_deg_l = []
    for line in file:
        line = line.strip()
        sing_deg_l.append(line)
    return sing_deg_l

def ensdarg_to_term_deg(sing_deg_l, zfin_anatomy_d):
    """convert DEG to anatomy_term"""
    uncounted_deats_l = []
    for ensdarg in sing_deg_l:
        if ensdarg in zfin_anatomy_d:
            for anat_term in zfin_anatomy_d[ensdarg]:
                uncounted_deats_l.append(anat_term)
    return uncounted_deats_l

def terms_counter_deg(uncounted_deat_l):
    """take a frequency count of terms"""
    term_counts_dict = {}
    for term in uncounted_deat_l:
        if term not in term_counts_dict:
            term_counts_dict[term] = 1
        else:
            term_counts_dict[term] += 1
    return term_counts_dict

#Multi DEG Functions
def mkdegs_dict(file):
    """creates three dictionaries: 1) cluster:[(ensdarg,pete_score),(ensdarg,pete_score)], 2) file pointers for data files, 3) file pointers for metadata files"""
    m_deg_d = {}
    data_fp_d = {}
    metadata_fp_d = {}
    for line in file:
        if "p_val" not in line:
            list=line.strip().split() #list[6] is cluster, list[7] is ENSDARG, list[8] p1/p2*lf score
            lfc = float(list[2])
            pct1 = float(list[3])
            pct2 = float(list[4])
            cluster_num = str(int(list[6])+1) #Add one to start cluster count at 1
            ensdarg = list[7]
            # print(pct2)
            if pct2 == 0.0:
                pct2 = 1e-10
                # list.append((pct1/pct2*lfc) #pct1/pct2*lfc
                tup = (ensdarg,(pct1/pct2*lfc))
                if cluster_num not in m_deg_d:
                    m_deg_d[cluster_num] = []
                    m_deg_d[cluster_num].append(tup)
                else:
                    m_deg_d[cluster_num].append(tup)
            else:
                tup = (ensdarg,(pct1/pct2*lfc))
                if cluster_num not in m_deg_d:
                    m_deg_d[cluster_num] = []
                    m_deg_d[cluster_num].append(tup)
                else:
                    m_deg_d[cluster_num].append(tup)
            data_fp = open("data/{0}.csv".format(cluster_num),"w") 
            data_fp_d[cluster_num] = data_fp
            metadata_fp = open("meta_data/{0}.csv".format(cluster_num),"w")
            metadata_fp_d[cluster_num] = metadata_fp
    return m_deg_d, data_fp_d, metadata_fp_d

def filter_degs(multi_degs_d, pete_score):
    ensdarg_sorted_l = []
    #sort tups
    for cluster in multi_degs_d:
        ensdarg_tup_l = multi_degs_d[cluster]
        ensdarg_tup_l.sort(key = lambda x: x[1], reverse=True)
        multi_degs_d[cluster] = ensdarg_tup_l
    #discard pete_scores
    for cluster in multi_degs_d:
        ensdarg_l = []
        for tup in multi_degs_d[cluster]:
            ensdarg_l.append(tup[0])
            multi_degs_d[cluster] = ensdarg_l
    for cluster in multi_degs_d:
        list_length = len(multi_degs_d[cluster])
        if list_length <= pete_score or pete_score == 0:
            multi_degs_d[cluster] = multi_degs_d[cluster]
        else:
            multi_degs_d[cluster] = multi_degs_d[cluster][:pete_score]
    return multi_degs_d

def ensdarg_to_term_degs(filtered_degs_d, zfin_anatomy_d):
    for cluster in filtered_degs_d: #{1:[ensdarg,ensdarg]}
        anat_terms_l = []
        for ensdarg in filtered_degs_d[cluster]:
            if ensdarg in zfin_anatomy_d:
                for anat_term in zfin_anatomy_d[ensdarg]:
                    anat_terms_l.append(anat_term)
                filtered_degs_d[cluster] = anat_terms_l
    return filtered_degs_d

def terms_counter_degs(uncounted_deat_d):
    """counts the number of unique term in a dictionary"""
    for cluster in uncounted_deat_d:
        term_counts_dict = {}
        for term in uncounted_deat_d[cluster]:
            if term not in term_counts_dict:
                term_counts_dict[term] = 1
            else:
                term_counts_dict[term] += 1
        uncounted_deat_d[cluster] = term_counts_dict
    return uncounted_deat_d
