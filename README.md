1. try_petrarch.py will send data to petrarch to extract event from sentences
2. similarity_finder.py is used to find the similarity between sentences using en_core_web_lg 
   which has 685k unique vectors (300 dimensions)
3. petrarch_validator.py will extract event from the initial data and then compute
   the similarity and save the score to the final.csv file