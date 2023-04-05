from flask import Flask
from flask import render_template, request, redirect, url_for, session
from forms import SearchForm
import math
from tfidf import search as Searching
import mysql.connector

connection = mysql.connector.connect(host='localhost',port='3306',database='rekomendasi_umkm',user='root',password='')
cursor = connection.cursor()

app = Flask(__name__)
app.secret_key = 'development'

@app.route("/")
def index():
    form = SearchForm()
    conn = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='rekomendasi_umkm')
    form = SearchForm()
    query = "SELECT * FROM list"
    cursor2 = conn.cursor()
    cursor2.execute(query)
    data = cursor2.fetchall()
    data_length = len(data)
    return render_template("index.html", form=form, data=data, len=data_length)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM user WHERE username=%s AND password=%s', (username, password))
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['id'] = record[0]
            session['username'] = record[1]
            form = SearchForm()
            msg = 'Logged in successfully !'
            conn = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='rekomendasi_umkm')
            
            query = "SELECT * FROM list"
            cursor2 = conn.cursor()
            cursor2.execute(query)
            data = cursor2.fetchall()
            data_length = len(data)
            print(data_length)
            return render_template('admin/index.html', msg=msg, form=form, data=data, len=data_length)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login/login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    form = SearchForm()
    return render_template("index.html", form=form)

@app.route("/searchRecomendation")
def searchRecomendation():
    form = SearchForm()
    query = request.args.get('keyword')

    # for pagination purpose
    if not request.args.get('page'):
        page = 1
    else:
        page = int(request.args.get('page'))

    # use tf.idf to search relevant document in query
    data = Searching.search_for(query)
    data_length = len(data)

    pagination_size = 8

    start = (page - 1) * pagination_size
    if (page * pagination_size) > data_length:
        end = data_length
    else:
        end = page * pagination_size
    total = math.ceil(data_length / pagination_size)

    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    cursor4 = conn.cursor()
    
    nama_produk = []
    for i in range(data_length):
        nama_produk.append(data[i][1])

    if (len(nama_produk)) > 0:

        nama_produk_length = len(nama_produk)
        test = list(nama_produk)
        values = [list([item]) for item in nama_produk]
        for i in range(nama_produk_length):
            sql="INSERT INTO history (nama_produk) VALUES (%s)"
            val=(list(values[i]))
            cursor4.execute(sql,val)
            conn.commit()
    
    return render_template("index_with_recomendation.html", form=form, data=data, keyword=query, page=page, start=start, end=end, total=total)

@app.route("/search")
def search():
    form = SearchForm()
    query = request.args.get('keyword')
    
    # for pagination purpose
    if not request.args.get('page'):
        page = 1
    else:
        page = int(request.args.get('page'))

    # use tf.idf to search relevant document in query
    data = Searching.search_for(query)
    data_length = len(data)

    pagination_size = 6

    start = (page - 1) * pagination_size
    if (page * pagination_size) > data_length:
        end = data_length
    else:
        end = page * pagination_size
    total = math.ceil(data_length / pagination_size)

    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    cursor5 = conn.cursor()
    
    nama_produk = []
    for i in range(data_length):
        nama_produk.append(data[i][1])

    if (len(nama_produk)) > 0:
        nama_produk_length = len(nama_produk)
        values = [list([item]) for item in nama_produk]
        for i in range(nama_produk_length):
            sql="INSERT INTO history (nama_produk) VALUES (%s)"
            val=(list(values[i]))
            cursor5.execute(sql,val)
            conn.commit()

    """queryRecommend = SELECT nama_produk, LOWER(REPLACE(nama_produk, ' ', '+' )) as link FROM history GROUP BY nama_produk ORDER BY RAND () LIMIT 7"""
    queryRecommend = "SELECT nama_produk, LOWER(REPLACE(nama_produk, ' ', '+' )) as link FROM history WHERE nama_produk LIKE "+"'%"+query+"%'"+" GROUP BY nama_produk LIMIT 7"
    cursor2 = conn.cursor()
    cursor2.execute(queryRecommend)
    recommend = cursor2.fetchall()
    strRecommend = len(recommend)

    return render_template("search.html", form=form, data=data, keyword=query, page=page, start=start, end=end, total=total, recommend=recommend, strRecommend=strRecommend)

@app.route('/listUmkm')
def listUmkm():
    msg = ''
    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    form = SearchForm()
    query = "SELECT * FROM list"
    cursor2 = conn.cursor()
    cursor2.execute(query)
    data = cursor2.fetchall()
    data_length = len(data)
    return render_template('admin/index.html', msg=msg, form=form, data=data, len=data_length)
    
@app.route('/formTambahData')
def formTambahData():
    return render_template('admin/form_tambah_data.html')

@app.route('/aksiTambah', methods =['GET', 'POST'])
def aksiTambah():
    """ Form Request """
    nama_produk = request.form['nama_produk']
    bahan_utama = request.form['bahan_utama']
    varian = request.form['varian']
    jenis_produk = request.form['jenis_produk']
    tipe_produk = request.form['tipe_produk']
    asal_daerah = request.form['asal_daerah']
    kesulitan = request.form['kesulitan']
    harga = request.form['harga']
    status_popular = request.form['status_popular']
    level_popular = request.form['level_popular']
    popular_di = request.form['popular_di']
    modal = request.form['modal']
    tempat_penjual = request.form['tempat_penjual']
    rating = request.form['rating']
    url = request.form['url']
    msg= ''
    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    sql="INSERT INTO list (nama_produk,bahan_utama,varian,jenis_produk,tipe_produk,asal_daerah,kesulitan,harga,status_popular,level_popular,popular_di,modal,tempat_penjual,rating,url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val=(nama_produk,bahan_utama,varian,jenis_produk,tipe_produk,asal_daerah,kesulitan,harga,status_popular,level_popular,popular_di,modal,tempat_penjual,rating,url)
    cursor1 = conn.cursor()
    cursor1.execute(sql,val)
    conn.commit()
    return redirect(url_for('listUmkm'))

@app.route('/formEdit/<id>')
def formEdit(id):
    idEdit = id
    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    query = "SELECT * FROM list WHERE id="+idEdit
    cursor3 = conn.cursor()
    cursor3.execute(query)
    data = cursor3.fetchall()
    print(data[0])
    return render_template('admin/form_edit_data.html', data=data)

@app.route('/aksiEdit', methods =['GET', 'POST'])
def aksiEdit():
    """ Form Request """
    id = request.form['id']
    nama_produk = request.form['nama_produk']
    bahan_utama = request.form['bahan_utama']
    varian = request.form['varian']
    jenis_produk = request.form['jenis_produk']
    tipe_produk = request.form['tipe_produk']
    asal_daerah = request.form['asal_daerah']
    kesulitan = request.form['kesulitan']
    harga = request.form['harga']
    status_popular = request.form['status_popular']
    level_popular = request.form['level_popular']
    popular_di = request.form['popular_di']
    modal = request.form['modal']
    tempat_penjual = request.form['tempat_penjual']
    rating = request.form['rating']
    url = request.form['url']
    msg= ''
    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    cursor1 = conn.cursor()
    """ Insert Data """
    sql="UPDATE list SET nama_produk = %s, bahan_utama = %s,varian = %s, jenis_produk = %s, tipe_produk = %s, asal_daerah = %s, kesulitan = %s, harga = %s, status_popular = %s, level_popular = %s, popular_di = %s, modal = %s, tempat_penjual = %s, rating = %s, url= %s WHERE id = %s"
    val=(nama_produk,bahan_utama,varian,jenis_produk,tipe_produk,asal_daerah,kesulitan,harga,status_popular,level_popular,popular_di,modal,tempat_penjual,rating,url,id)
    cursor1.execute(sql,val)
    conn.commit()
    return redirect(url_for('listUmkm'))
    

@app.route('/aksiHapus/<id>')
def aksiHapus(id):
    msg=''
    idHapus = id
    conn = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='rekomendasi_umkm')
    query = "DELETE FROM LIST WHERE id="+idHapus
    cursor3 = conn.cursor()
    cursor3.execute(query)
    conn.commit()
    return redirect(url_for('listUmkm'))


if __name__ == '__main__':
   app.run(debug = True)
