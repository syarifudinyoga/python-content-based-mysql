"""
indexing.py is for index all document in database
so it will index all unique keyword and store in one file called index.txt
run the indexing.py again when you add some stuff in database
"""

import mysql.connector
import re
from operator import itemgetter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


def create_connection():
    """ create MySQL connection """

    conn = mysql.connector.connect(user='root', password='',
            host='127.0.0.1',
            database='rekomendasi_umkm')

    return conn


def get_data_docs(conn):
    """ get document data from DB """

    output = []

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM list")
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
        text = doc[2]
        text = text.lower()
        text = re.sub('[^A-Za-z]+', ' ', text)
        contents.append(text)

    return contents


def tokenizing(docs):
    """ function for tokenize the string """
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
        token = [text for text in token if text not in conjunctions]
        tokens.append(token)

    return tokens


def get_index(tokens):
    """ function for get all unique keyword in document """

    uniq_token = [val for token in tokens for val in token]
    uniques = sorted(list(set(uniq_token)))
    return uniques

def main():
    conn = create_connection()
    docs = get_data_docs(conn)
    conn.close()

    contents = get_content(docs)
    tokens = tokenizing(contents)
    indices = get_index(tokens)

    # save to file
    with open('index.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % keyword for keyword in indices)

    print("Indexing success!")


if __name__ == "__main__":
    main()

