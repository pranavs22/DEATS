## DEATS
TITLE: Differential Expression Anatomy Term Sheets

AUTHORS: Paula Berry, Severiano Villarruel, Pranav Sahasdrabudhe

AFFILIATION: University of Oregon

VERSION 1.00

## Overview
### How the DEATS Generator Works

By reviewing scientific research, the ZFIN database has been gathering data that connects zebrafish genes (starting with ENSDARGs) to zebrafish anatomy (ZFA & BSPO). The DEATS Generator leverages this information to help label unidentified cell-types from single-cell RNA seq. Our program goes into the ZFIN database, finds the zebrafish anatomy associated with the zebrafish genes the user has input, and generates a differentially expressed anatomy term sheet, or DEATS, table, displaying which anatomy terms are associated with the input and how many times these anatomy terms were found. 

### Why make a DEATS table?
DEATS tables were envisioned by the ZFIN organization as a method for labeling unidentified cell-types using single-cell RNA sequencing data. Single-cell RNA sequencing data, which can show genes differentially expressed between cell-types, provide tremendous insight into the differences between an organism, or a tissue’s, cell-types. Unfortunately, one of the things currently unautomated is the use of data to label the cell-types present organism or tissue. The DEATS generator looks to solve this problem by using the expertly curated ZFIN database to create a simple table which shows the anatomy most often associated with the cell-types differentially expressed genes. In most cases the top values in the DEATS table can be used to determine a suitable label for the unidentified cell-type of interest.
This program uses the published anatomical locations of a gene's expression and a list of Differentially Expressed Genes for a Cell-Type to create a Differentially Expressed Anatomy Terms Sheet (DEATS). DEATS can be used to annotate one or multiple zebrafish cell-types.

## Terms
#### Pete Score:  
  Ratio of (Pct-1/ Pct-2) * Avg Log FC
Where, 
Pct1 – Percentage of genes differentially expressed in a cluster
Pct2 – Percentage of genes differentially expressed in all cluster
Avg Log FC – Average Log Fold Change

### 2.How to use this tool:
#### 1.	Inputs
a.	Choose Developmental stage you are interested in, from the drop-down menu.
e.g.

In this example, we choose All Stages.
b.	Upload a list of Differentially Expressed Genes OR Multiple DEG Lists
In this example, we choose ‘Click here for an example DEG List’  option.
Snapshot
c.	You can also use sample list which is already loaded in the box.

#### 2.	Choose PETE score. More explanation of PETE score can be found in section ‘TERMS’
 
#### 3.	Run!
Click on the *Go* button to start your data annotation.

#### 4.	Results
Based on Pete score, the program ranks the genes in each cluster in ascending order.
There are total 3 outputs:

#### 1.	Anatomy Term---2.Count---3. P value
Example snapshot:
	 

This program outputs list of anatomy terms associated with a particular cell cluster. 
All the results are in the tab called **DEATS**. Move over to the DEATS tab to view the results. 
The user can view as well as download the results as per the number of clusters through **Download DEATS** button.
 
If the user is interested in a particular annotation term, the user has an option to search for the terms in cell-type annotation search-box
 
On the top-right corner, user also has an option to view Gene symbols by clicking **See Gene Symbols** button.

