"""
calculate_tfidf.py is tf.idf based text mining algorithm that use in search engine
this file is main of tf.idf calculation, and return the result of relevant document
that already sorted by its score
"""
from bs4 import BeautifulSoup
import mysql.connector
import urllib.request
import sys
import re
import math
from operator import itemgetter

def create_connection():
    """ create MySQL connection """    
    conn = mysql.connector.connect(user='root', password='',
            host='127.0.0.1',
            database='rekomendasi_umkm')

    return conn


def get_data_docs(conn, keyword):
    """ get document data from DB """

    param = "|".join(keyword)
    output = []

    """ query = "SELECT * FROM list WHERE nama_produk REGEXP '" + param + "' OR bahan_utama REGEXP '" + param + "' OR asal_daerah REGEXP '" + param + "' OR level_popular REGEXP '" + param + "' OR modal REGEXP '" + param + "'" """
    query = "SELECT * FROM list WHERE nama_produk REGEXP '" + param + "' OR jenis_produk REGEXP '" + param + "' OR modal REGEXP '" + param + "' OR popular_di REGEXP '" + param + "' OR asal_daerah REGEXP '" + param + "'"

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        output.append(list(row))

    return output


def get_content(docs):
    """ 
    get only content of document 
    and format it to lower case and remove all special chars
    """
    contents = []

    for doc in docs:
        text = doc[4]
        text = text.lower()
        text = re.sub('[^A-Za-z]+', ' ', text)
        contents.append(text)

    return contents


def tokenizing(docs):
    """ function for tokenize the string """

    """ conjunctions = ['for',  'But', 'Or', 'Yet',
            'So', 'After', 'Although', 'As', 'As if', 'Because', 'Before',
            'Even', 'only', 'Lest', 'Now', 'Once', 'Provided', 'Since',
            'Supposing', 'Than', 'That', 'Though', 'Till', 'Until', 'When',
            'Whenever', 'Where', 'Whereas', 'Wherever', 'Whether', 'Which', 'While', 'Who', 'Whoever	',
            'Why', 'Both', 'and', 'Finally', 'Meanwhile', 'Instead', 'Indeed',
            'Incidentally', 'Likewise']
    """
    conjunctions = ['dan','lagipula','serta','sebelumnya','selanjutnya','bilamana',
            'sejak','sesudah','tetapi','melainkan','sedangkan','atau','ataupun','maupun',
            'guna','untuk','agar','supaya','sebab','karena','sehingga',
            'sampai','akibatnya','lalu','kemudian','jika','jikalau',
            'kalau','apabila','walaupun','meskipun','biarpun','seperti',
            'sebagai','bagai','bagaikan','walau','walaupun','meskipun',
            'biar','biarpun','sehingga','bukannya','bahkan',
            'apalagi','yaitu','yakni','kecuali','selain','asal','bahwa']

    tokens = []
    for doc in docs:
        token = doc.split(" ")
        token = list(filter(None, token))
        # FILTERING
        token = [text for text in token if text not in conjunctions]
        tokens.append(token)
    
    return tokens


def tfidf(tokens):
    """ function for calculate tf.idf """

    tables = []
    N = len(tokens)

    uniq_token = [val for token in tokens for val in token]
    uniques = sorted(list(set(uniq_token)))

    for token in tokens:
        table = {k:0 for k in uniques}
        for key in token:
            if key in table:
                table[key] += 1
        tables.append(table)

    # calculate df
    df_table = {k:0 for k in uniques}
    for table in tables:
        for key in table:
            if table[key] != 0:
                df_table[key] += 1

    # calculate idf
    idf_table = {k:0 for k in uniques}
    for key in idf_table:
        idf_table[key] = (1 + math.log10((N / df_table[key])))

    # calculate tf.idf
    tfidf_table = []
    for table in tables:
        temp_table = {k:0 for k in uniques}
        for key in table:
            if table[key] != 0:
                temp_table[key] = table[key] * idf_table[key]
        tfidf_table.append(temp_table)

    return tfidf_table


def search_keyword(q, docs, tfidf_table):
    """ 
    function for search in tf.idf table by keyword 
    calculate the score from every document that contain the keyword
    and sort the document by high score
    """

    scores = []

    for obj in tfidf_table:
        score = 0
        for key in obj:
            if key in q:
                score += obj[key]
        scores.append(score)
    
    """ print(scores) """

    for x in range(len(scores)):
        docs[x].append(scores[x])

    sorted_doc = sorted(docs, key=itemgetter(16), reverse=True)
    return sorted_doc


def get_result(keyword):
    """ call this (main) function to calculate tf.idf """
    conn = create_connection()
    docs = get_data_docs(conn, keyword)
    conn.close()

    contents = get_content(docs)
    tokens = tokenizing(contents)
    tfidf_table = tfidf(tokens)
    result = search_keyword(keyword, docs, tfidf_table)

    return result
