#-------------------------------------------------------------------------
# AUTHOR: Michael Phu
# FILENAME: db_connection_mongo.py
# SPECIFICATION: A program that communicates with a MongoDB database to create documents,
#               delete documents, update documents, and return the inverted index of a collection.  
# FOR: CS 4250 - Assignment #2
# TIME SPENT: 1 Hour
#-----------------------------------------------------------*/

#importing some Python libraries
from pymongo import MongoClient  # import mongo client to connect
import string
from dateutil.parser import parse

def connectDataBase():

    # Creating an instance of mongoclient and informing the connection string
    client = MongoClient(host=['localhost:27017'])
    # Creating database
    db = client.corpus

    return db 

def createDocument(db, docId, docText, docTitle, docDate, docCat):

    # Get num_chars for doc text
    num_chars = get_num_chars(docText)

    # Put all terms in text into an array. " " is the delimiter. 
    translator = str.maketrans('', '', string.punctuation)
    term_list = [term.lower() for term in (str(docText).translate(translator)).split(' ')]

    # Store term and occurrence count in a dictionary
    dic1 = {}
    for term in term_list: 
        if term in dic1:
            dic1[term] += 1
        else:
            dic1[term] = 1

    # Add term dictionaries to the final "terms" field
    terms = []
    for term in dic1:
        dic2 = {}
        dic2["term"] = term
        dic2["count"] = dic1[term]
        dic2["num_chars"] = get_num_chars(term)
        terms.append(dic2)
        
    # Parse date... 
    dt = parse(docDate)
    dt = dt.strftime('%Y-%m-%d')

    # Create document object 
    document = {
        "doc_number": int(docId),
        "text": docText, 
        "title": docTitle,
        "num_chars": int(num_chars),
        "date": dt,
        "category": docCat,
        "terms": terms 
    }

    # Insert document 
    db.insert_one(document)

def deleteDocument(db, docId):

    # Delete the document from the database 
    db.delete_one({"doc_number": int(docId)})

def updateDocument(db, docId, docText, docTitle, docDate, docCat):

    # Delete the document 
    deleteDocument(db, docId)

    # Create new document with updated information
    createDocument(db, docId, docText, docTitle, docDate, docCat)

def getIndex(db):

    # Initialize index
    index = {}

    # Get all documents, exclude _id 
    documents = list(db.find({},{"_id":0}))
    
    # Generate index 
    for doc in documents:
        
        # Add term occurences to index 
        for term_dic in doc["terms"]:
            term = term_dic["term"]
            count = term_dic["count"]
            x = doc["title"] + ':' + str(count)
            if term in index:
                 index[term] += ',' + x
            else:
                 index[term] = x
                 
    return index
   
def get_num_chars(s): 

    num_chars = 0 

    for char in s:
        if char.isalpha():
            num_chars += 1
    
    return num_chars

    


