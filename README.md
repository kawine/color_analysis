# Color Analysis

This project is an analysis of color in 19th century literature, done in concert with the Literary Lab at Stanford University.


File List:

color_analysis.py 
	- Run main method to build the databases. This takes a long time and is currently spread over 22 threads. Run merge_databases() to merge the newly created databases into a single one called color_analysis_merged.db

storage.py
	- Contains methods for insertion into the smaller databases (one for each thread). 

sentence.py
	- Extracts the salient features from each sentence.

book.py
	- Processing an entire book. Contains preprocessing methods and the parse_book method for parsing an entire book.

metadata.p
	- A pickled dictionary with the metadata (i.e. title, author, and year published) for each book. Indexed by file names ending in _tokenized.txt.

extended_colors.csv
	- List of all valid colors and relevant properties. Colors may be added to the program's internal list ad hoc, but such bootstrapped colors are not then added to this csv file, which was manually prepared.

schema.txt
	- Schema for the database. For more info, see storage.py


To be added:

color_analysis_merged.db
	- The database with all the relevant data (called 'merged' because the processing is multi-threaded, and so many databases are merged to form this one). Schema can be found in schema.txt.

