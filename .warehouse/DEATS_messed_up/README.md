## DEATS
TITLE: Differential Expression Anatomy Term Sheets

AUTHORS: Paula Berry, Severiano Villarruel, Pranav Sahasrabudhe

AFFILIATION: University of Oregon

VERSION 1.00

## Overview
### How the DEATS Generator Works

By reviewing scientific research, the ZFIN database has been gathering data that connects zebrafish genes (starting with ENSDARGs) to zebrafish anatomy (ZFA & BSPO). The DEATS Generator leverages this information to help label unidentified cell-types from single-cell RNA seq. Our program goes into the ZFIN database, finds the zebrafish anatomy associated with the zebrafish genes the user has input, and generates a differentially expressed anatomy term sheet, or DEATS, table, displaying which anatomy terms are associated with the input and how many times these anatomy terms were found. 

### Why make a DEATS table?
DEATS tables were envisioned by the ZFIN organization as a method for labeling unidentified cell-types using single-cell RNA sequencing data. Single-cell RNA sequencing data, which can show genes differentially expressed between cell-types, provide tremendous insight into the differences between an organism, or a tissue’s, cell-types. Unfortunately, one of the things currently unautomated is the use of data to label the cell-types present organism or tissue. The DEATS generator looks to solve this problem by using the expertly curated ZFIN database to create a simple table which shows the anatomy most often associated with the cell-types differentially expressed genes. In most cases the top values in the DEATS table can be used to determine a suitable label for the unidentified cell-type of interest.
This program uses the published anatomical locations of a gene's expression and a list of Differentially Expressed Genes for a Cell-Type to create a Differentially Expressed Anatomy Terms Sheet (DEATS). DEATS can be used to annotate one or multiple zebrafish cell-types.

#### To know more about the tool, please refer to the user manual document in this repository 
<a href="https://github.com/pranavs22/DEATS/blob/master/DEATS-%20User%20Manual.pdf">User Manual</a>

