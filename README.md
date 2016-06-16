# Color Analysis

This project is an analysis of color in 19th century literature, done in concert with the Literary Lab at Stanford University. Please contact Irena Yamboliev (firstname[at]stanford.edu) or Kawin Ethayarajh ([firstname][at]cs.toronto.edu) if you'd like to contribute.


### File List:

<dl>
  <dt>color_analysis.py</dt>
  <dd>- Run main method to build the databases. This takes a long time and is currently spread over 22 threads. Run merge_databases() to merge the newly created databases into a single one called color_analysis_merged.db</dd>

  <dt>storage.py</dt>
  <dd>Contains methods for insertion into the smaller databases (one for each thread).</dd>

  <dt>sentence.py</dt>
  <dd>Extracts the salient features from each sentence.</dd>

  <dt>book.py</dt>
  <dd>Processing an entire book. Contains preprocessing methods and the parse_book method for parsing an entire book.</dd>

  <dt>metadata.p</dt>
  <dd>A pickled dictionary with the metadata (i.e. title, author, and year published) for each book. Indexed by file names ending in _tokenized.txt.</dd>

  <dt>extended_colors.csv</dt>
  <dd>List of all valid colors and relevant properties. Colors may be added to the program's internal list ad hoc, but such bootstrapped colors are not then added to this csv file, which was manually prepared.</dd>

  <dt>schema.txt</dt>
  <dd>Schema for the database. For more info, see storage.py</dd>
</dl>


### To be added:

<dl>
  <dt>color_analysis_merged.db</dt>
  <dd>The database with all the relevant data (called 'merged' because the processing is multi-threaded, and so many databases are merged to form this one). Schema can be found in schema.txt.</dd>
</dl>
