from pymongo import MongoClient

global db_client
try:
	db_client
except NameError:
	db_client = MongoClient('mongodb://guest:guest@askcos2.mit.edu/admin', 27017)
	#print(db_client.database_names())