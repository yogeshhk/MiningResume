# MiningResume
Script to extract certain fields from a text resume
Copyright (C) 2017 Yogesh H Kulkarni

## License:
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or any later version.

## Requirements:
* Problem Statement: Extracting certain important fields from a resume like name, email, phone,  etc.
* resume_config.xml specifies fields to extract along with the patterns to look for those fields, respetively.
* parser.py take the config file as well as the directory having text resumes, as arguments.
* As all the domain (resume, here) is specified in the config file, any changes or addition to logic is done only the the config file. 
* (Ideally) parser logic is independant and thus should not need any change. Atleast thats the idea!!
* Certain field etxraction methods are specified in the config file which are used to parse based on the pattern specified.

## Dependencies:
* Needs Python 2.7

## How to Run:
* Prepare your own config.xml similar to the given one. 
* Run as "parser.py config datadir"

## Disclaimer:
* Author (yogeshkulkarni@yahoo.com) gives no guarantee of the results of the program. It is just a fun script. Lot of improvements are still to be made. So, don’t depend on it at all.
