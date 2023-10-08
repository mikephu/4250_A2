#-------------------------------------------------------------------------
# AUTHOR: Michael Phu
# FILENAME: db_connection.py
# SPECIFICATION: A program that communicates with a PostgreSQL database to create categories,
#               create documents, delete documents, update documents, and the index between 
#               term and document tables. 
# FOR: CS 4250 - Assignment #2
# TIME SPENT: 3 Hours
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
import string
import psycopg2
from psycopg2.extras import RealDictCursor

def connectDataBase():

    # Create a database connection object using psycopg2
    DB_NAME = "CPP"
    DB_USER = "postgres"
    DB_PASS = "123"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT,
                                cursor_factory=RealDictCursor)    
        return conn
    except:
        print("Database not connected successfully")
   
def createCategory(cur, catId, catName):

    # Insert a category in the database
    sql = "INSERT INTO category (category_id, name) VALUES (%(catId)s,%(catName)s)"
    var = {'catId':catId,"catName":catName}
    cur.execute(sql,var)

def createDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Get the category id based on the informed category name
    sql = "SELECT category_id FROM category WHERE name = %(docCat)s"
    cur.execute(sql,{"docCat":docCat}) 
    recset = cur.fetchall()
    category_id = recset[0]["category_id"]
    
    # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
    num_chars = 0 
    for char in docText:
        if char.isalpha():
            num_chars += 1

    sql = """INSERT INTO document (doc_number, category_id, text, title, num_chars, date)
             VALUES (%(docId)s,%(c_id)s,%(text)s,%(title)s,%(num_chars)s,%(date)s)"""
    
    var = {"docId":docId,"c_id":category_id,"text":docText,"title":docTitle,"num_chars":num_chars,"date":docDate}

    cur.execute(sql,var)

    # 3 Update the potential new terms.
    # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
    # 3.2 For each term identified, check if the term already exists in the database
    # 3.3 In case the term does not exist, insert it into the database
    translator = str.maketrans('', '', string.punctuation)
    term_list = (str(docText).translate(translator)).split(' ')
    for term in term_list:
        sql = "SELECT * FROM term WHERE term = %(term)s"
        cur.execute(sql,{"term":term})
        recset2 = cur.fetchall()
        if not recset2:
            sql = "INSERT INTO term (term, num_chars) VALUES (%(term)s,%(num_chars)s)" 
            cur.execute(sql,{"term":term,"num_chars":len(term)})

    # 4 Update the index
    # 4.1 Find all terms that belong to the document
    # 4.2 Create a data structure the stores how many times (count) each term appears in the document
    # 4.3 Insert the term and its corresponding count into the database
    dic = {}
    for term in term_list: 
        if term in dic:
            dic[term] += 1
        else:
            dic[term] = 1

    for term in dic:
        sql = "INSERT INTO index (doc_number, term, count) VALUES (%(doc_id)s,%(term)s,%(count)s)"
        cur.execute(sql,{"doc_id":docId,"term":term,"count":dic[term]})

def deleteDocument(cur, docId):
    
    # 1 Query the index based on the document to identify terms
    sql = "SELECT term FROM index WHERE doc_number = %(docId)s"
    cur.execute(sql,{"docId":docId})
    recset = cur.fetchall()    

    # 1.1 For each term identified, delete its occurrences in the index for that document
    for row in recset: 
        sql = "DELETE FROM index WHERE doc_number = %(docId)s AND term = %(term)s"
        cur.execute(sql,{"docId":docId,"term":row["term"]})
    
    # 1.2 Check if there are no more occurrences of the term in another document. 
    #     If this happens, delete the term from the database.
    for row in recset:
        sql = "SELECT term FROM index WHERE term = %(term)s"
        cur.execute(sql,{"term":row["term"]})
        termset = cur.fetchall()
        if not termset:
            sql = "DELETE FROM term WHERE term = %(term)s"
            cur.execute(sql,{"term":row["term"]})
    
    # 2 Delete the document from the database
    sql = "DELETE FROM document WHERE doc_number = %(docId)s"
    cur.execute(sql,{"docId":docId})

def updateDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Delete the document
    deleteDocument(cur,docId)
    
    # 2 Create the document with the same id
    createDocument(cur, docId, docText, docTitle, docDate, docCat)

def getIndex(cur):
    
    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    sql = "SELECT * FROM index"
    cur.execute(sql)
    recset = cur.fetchall()
    res = {}

    for row in recset:
        sql = "SELECT title FROM document WHERE doc_number = %(docId)s"
        cur.execute(sql,{"docId":row["doc_number"]})
        title = str(cur.fetchall()[0]["title"])
        if row["term"] in res:
            res[row["term"]] += ',' + title + ':' + str(row["count"])
        else:
            res[row["term"]] = title + ':' + str(row["count"])

    return res 

    
    