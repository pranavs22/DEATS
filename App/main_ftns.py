#!/usr/bin/env python3

def parse_records(record):
    anatomy_id = []
    ensdarg = None
    for item in record:
        if item == "ensemblCrossReferences":
            if record[item] != []:
                ensdarg = record[item][0]["id"]
                ensdarg = ensdarg.split(":")[1]
            # else:
            #     ensdarg = "NA"
        if item == "geneSymbol":
            gene_symbol = record[item]
        if item =="geneName":
            gene_name = record[item]
        #GET STAGE NAME FROM JSON RECORD
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
    # if ":" or " " in dev_stage:#
    #     dev_stage = dev_stage.replace(":","_").replace(" ","_")#
    return ensdarg, gene_symbol, gene_name, dev_stage, anatomy_id

def sort_tuple_list_by_second_item(ensdarg_list):
    """reads in lines from biomarkers table. returns a list for each cluster, the list is in order of the highest p1/p2*lf."""
    ensdarg_list.sort(key = lambda x: x[1], reverse=True)
    return ensdarg_list

def flatten_sorted_list(ensdarg_list_tuples):
    ensdarg_sorted_list = []
    for tup in ensdarg_list_tuples:
        ensdarg_sorted_list.append(tup[0])
    return ensdarg_sorted_list

def top_items_or_less(ensdarg_sorted_list, number):  #BUGGED
    list_length = len(ensdarg_sorted_list)
    if list_length <= number:
        filtered_ensdarg_lst = ensdarg_sorted_list
    else:
        filtered_ensdarg_lst = ensdarg_sorted_list[:number]
    return filtered_ensdarg_lst

def convert_ensdarg_list_to_anatomy_id_list(ensdargs_list, ensdarg_anatomy_id_dictionary):
    """takes in a list of ensdargs and converts them to a list of zfas"""
    zfa_lst = []
    for ensdarg in ensdargs_list:
        if ensdarg in ensdarg_anatomy_id_dictionary:
            zfa_lst.append(ensdarg_anatomy_id_dictionary[ensdarg])
    flat_list = []
    for sublist in zfa_lst:
        for item in sublist:
            flat_list.append(item)
    return flat_list

def convert_id_to_terms(id_list, zfa_to_terms_reference_dictionary,bspo_to_terms_reference_dictionary):
    """converts a list of anatomy_ids to a list of anatomy terms"""
    id_terms = []
    for id in id_list:
        if id in zfa_to_terms_reference_dictionary:
            id_terms.append(zfa_to_terms_reference_dictionary[id])
        if id in bspo_to_terms_reference_dictionary:
            id_terms.append(bspo_to_terms_reference_dictionary[id])
    return id_terms

def terms_counter(terms_list):
    """counts the number of unique term in a dictionary"""
    term_counts_dict = {}
    for term in terms_list:
        if term not in term_counts_dict:
            term_counts_dict[term] = 1
        else:
            term_counts_dict[term] += 1
    return term_counts_dict

def sort_id_counts_dict(cluster_dict):
    """reads in lines from biomarkers table. returns a list for each cluster, the list is in order of the highest p1/p2*lf."""
    cluster_dict = sorted(cluster_dict.items(), key=lambda kv: kv[1], reverse=True)
    return cluster_dict
