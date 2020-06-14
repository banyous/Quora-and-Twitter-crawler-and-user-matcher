
This repository helps in collecting true matching accounts between Quora and Twitter networks.

Please note that Quora and Twitter do change the layout/structure of its website every now and then. So please update the code in case it doesn't work as expected.

You can find a data-set of 27k true matching Quora-Twitter accounts produced by this code in the following link :
https://zenodo.org/record/3837711#.XuHpK5ZRVH4


_________________________________________________________________________________________

Our matching process is composed of three steps (modules):

## 1-Quora-scrapping
The goal of this module is to retieve Quora users IDs. We complete this by doing two steps:
1- We crawl Quora Questions URLs based on a set of Quora topics keywords file.
2- We crawl all Question's answers and extract the authors ( Quora users IDs) 

## 2-Matching-Quora-twitter-users
Based on the Quora users IDs extracted from the previous module, we perform an image matching algorithm in order to link the Quora accounts with their corresponding Twitter accounts. 

## 3-Crawl-twitter-quora-profiles
All the true matching Qu/Tw pairs verified from the  2-Matching-Quora-twitter-users will have their Twitter and Quora accounts crawled in this module.

Please note that each module can be used separetly.
A more detailed description of each module can be found in the notes.txt files within the correspondant folder.
*************************************************************************************************************
# Contact
For any question, please contact the main contributor:
* Youcef Benkhedda: y_benkhedda@esi.dz

# Acknowledgment
Thanks to the following people for their valuable feedback.
- Sofiane Abbar, QCRI
