
## ZFIN Differential Expressed Anatomy Terms Sheet Generator

## Overview
This program, DEATS, uses the published anatomical locations of a gene's expression as annotated by ZFIN (zANAT) and a set of Differentially Expressed Genes for a Cell-Type (DEG) to create an Differentially Expressed Anatomy Terms Sheet (DEATS). DEATS can be used to annotate a *single* or *multiple* zebrafish cell-types.

## File Structure
The structure of this app is as follows:

**Source Code**
- The 'app.R' file a) has the UI code, b) takes in the DEG, and c) contains the code used to pass information to and from the 'main.py' file
- The 'main.py' file runs the computation (i.e. links together the 'zfin_ftns.py' & the 'deats_ftns,py' files)
- The 'zfin_ftns.py' file has the functions to parse the zfin-data file
- The 'deats_ftns.py' file has the functions to create the deats table

**Directories**
- The 'files' directory has the logic operator files for the app.R code, the single 's_deg.csv' or multi 'm_deg.csv' file downloaded from the user in the app.R script, and the files for the 'main.py' (the zfin json, the zfa & bspo ids, the stagelabels id, the multi deg example set and the single deg example set)
- The 'data' directory contains the DEATS output (CSV files with the zANAT and its frequency count) 
- The 'meta_data' directory has the meta_data from the 'main.py' script. This data has the gene symbols and the ensdargs
- The 'sym_data' directory has the same thing as 'meta_data'. To make this directory meta_data is duplicated in the app.R script.(This action is taken because the information in 'sym_data' remains static while the information in 'meta_data' is subject to renaming.)
- The 'stats' directory has the term frequency counts for all of the zfin data (i.e. data from the JSON file)
- The 'www' directory has photos for the UI poprtion of the app.R scipt 

## Inputs
- Single set of differentially expressed genes (sDEG) OR multiple sets of differentially expressed genes (mDEG)
- JSON file with ZFIN data (zANAT)
- ZFA and BSPO zANAT labels
- Developmental stage labels (used to filter the applications zANAT terms)

### Single DEG List
Below is an example of the proper input format for a Single DEG List (sDEG)

### Multiple DEG Lists
Below is an example of the proper input format for a Multiple DEG Lists (mDEG). This format follows the format of the table produced using the FindMarkers function in Seurat.

## Outputs
This program's output is directed to a directory named "data" and a directory names "meta_data". If theses directories do not exist they must be created before the program is executed.

## Flags
1. multiple_sets: Path to file with multiple DEG sets (in the format described above)
2. single_set: Path to file with single DEG set (in the format described above)
3. stage: String of developmental stage of the organism. 'all stages' should be used if stage is unknown or no filter is desired.
4. pete_filt: Integer that contains the cut off of genes with the highest Pete Number. Cannot be used for Single DEG Set inputs.
5. zfin: Path to JSON file that contains format used here: http://zfin.org/downloads/zfin_wt_expression.json
6. zfa: Path to file that contains a list of ZFA IDs and their accociate Anatomy Terms
7. bspo: Path to file that contains a list of BSPO IDs and their accociate Anatomy Terms
8. stage_file: Path to file that contains all Developmental Stages existing in ZFIN

## Example Execution Commands
**Multiple DEG Lists**

./main.py \
-multiple_lists ../seurat_output/seurat_olig_ha_file.tsv \
-stage Larval_Protruding-mouth \
-zfin ../../zfin.json \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt

./main.py \
> -multiple_lists ../Seurat_Output/seurat_olig_ha_file.tsv \
> -stage all_stages \
> -zfin files/zfin_wt_expression.json \
> -zfa files/zfa_ids.txt \
> -bspo files/bspo_cleaned.txt \
> -stage_file files/stagelabel.txt \
> -pete 16
>
**Single DEG List**

./main.py \
-single_list files/deg.tsv \
-stage Larval_Protruding-mouth \
-zfin ../../zfin.json \
-zfa files/zfa_ids.txt \
-bspo files/bspo_cleaned.txt \
-stage_file files/stagelabel.txt
