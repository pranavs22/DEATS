## ZFIN Differential Expressed Anatomy Terms Sheet Generator

## Overview
This program uses the published anatomical locations of a gene's expression and a list of Differentially Expressed Genes for a Cell-Type to create an Differentially Expressed Anatomy Terms Sheet (DEATS). DEATS can be used to annotate one or multiple zebrafish cell-types.

## File Structure
The structure of this app is as follows:
- The 'main.py' file runs the computation (i.e. parses zfin data and creats the
  deats frequency table)
- The 'app.R' file has the ui code and the code that passes information to and
  from the 'main.py' file
- The 'data' directory has the deats table either for each cluster or for the
  list passed in
- The 'files' directory has the logic operator files for the app.R code, the
  single 'deg.tsv' or multi 'degs.tsv' files downloaded from the user in the app.R
  script, and the files for the 'main.py' (the zfin json, the zfa & bspo ids, the
  stagelabels id)
- The 'meta_data' directory has the meta_data from the 'main.py' script. This data has
  the gene symbols and the ensdargs
- The 'sym_data' directory has the same thing as 'meta_data'. To make this directory
  meta_data is directly copied over in the app.R script. This action is taken because
  the information in 'sym_data' remains static while the information in 'meta_data'
  is subject to renaming.
- The 'www' directory has photos for the ui poprtion of the app.R scipt 
- The 'stats' directory has the term frequency counts for all of the zfin data

## Inputs
Inputs to this program are either multiple lists of differentially expressed genes (DEG) per cell-type or a single DEG for a single cell-type.

### Single DEG List
Below is an example of the proper input format for a Single DEG List.

### Multiple DEG Lists
Below is an example of the proper input format for a Multiple DEG Lists. This format follows the format of the table produced using the FindMarkers function in Seurat.

## Outputs
This program's output is directed to a directory named "data" and a directory names "meta_data". If theses directories do not exist they must be created be fore the program is executed.

## Flags
1. multiple_lists: Path to file with multiple DEG lists (in the format described above)
2. single_list: Path to file with single DEG list (in the format described above)
3. stage: String of developmental stage of the organism. 'all stages' should be used if stage is unknown or no specification is desired.
4. pete_filt: Integer that contains the cut off of gene's with the highest Pete Number. Cannot be used for Single DEG List Inputs.
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
