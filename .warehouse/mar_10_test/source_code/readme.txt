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
  is subject to renaming
- The 'www' directory has photos for the ui poprtion of the app.R scipt 
- The 'stats' directory has the term frequency counts for all of the zfin data
