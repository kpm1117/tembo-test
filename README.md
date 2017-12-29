### Summary
* Just a basic API demonstrating access to a NoSQL database containing character profiles and stats from the Marvel universe.

### Firebase Credentials
* A crentials files must exist under /private/<filename> in order for the API to work correctly. This file contains a key that gives the API access to the relevant project. I will provide it separately.

### Additional Notes
* The FIRST APPEARANCE values in the source files contain two different date formats: Aaa-nn and [n]n-Aaa where a is alpha (for the year) and n is numeric (for the month). For consistency and sorting purposes, I converted to yyyy-mm.
* Some of the columns contained redundant language (e.g. Hair:Blond Hair) which I made an effort to reduce in the data_import ETL.
* Character names are a little confusing and often include info about which universe the character belongs to. This latter part should be a separate attribute, but I couldn't see a way to extract it unproblematically, at least not in the time alotted. This is one of those things I would want to consult with the client about.
* I did some normalization on the column names as well.
* My database stores stats as an attribute of each character. This is benificial in that it allow the API to provide all of a character's info without making multiple data pulls. But it also prevents the API from searching/filtering on stat values. The stats should really be stored in multiple structures (common with Firebase) to allow for a variety of queries.
* Regarding the firebase admin SDK: It does allow RESTful access to the database but I made some effort to demonstrate that I can design such functionality myself as well.