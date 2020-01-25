## ZFIN Differential Expressed Anatomy Terms Sheet Generator

## Overview
This program uses the published anatomical locations of a gene's expression and a list of Differentially Expressed Genes for a Cell-Type to create an Differentially Expressed Anatomy Terms Sheet (DEATS). DEATS can be used to annotate one or multiple zebrafish cell-types.

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
