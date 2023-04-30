# MiningResume
Script to extract certain fields from a text resume

Copyright (C) 2017 Yogesh H Kulkarni

## Requirements:
* Problem Statement: Extracting certain important fields from a resume like name, email, phone,  etc.
* config.xml specifies fields to extract along with the patterns to look for those fields, respectively.
* parser.py take the config file as well as the directory having text resumes, as arguments.
* As all the domain (resume, here) is specified in the config file, any changes or addition to logic is done only the the config file. 
* (Ideally) parser logic is independent and thus should not need any change. Atleast thats the idea!!
* Certain field extraction methods are specified in the config file which are used to parse based on the pattern specified.

## Dependencies:
* Needs Python 3+

## How to Run:
* Prepare your own config.xml similar to the given one. 
* Run "python parser.py"

## How to Run GUI:
* Install requirements
  ```
  pip install -r requirements.txt
  ```
* Run "python main.py"

## Disclaimer:
* Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.
