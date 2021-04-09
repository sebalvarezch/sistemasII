
#Impotando librerias a usar
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
import timeit
import datetime
from flask_mail import Mail, Message
import os
from wtforms.fields.html5 import EmailField

#Creando el objeto flask
app = Flask(__name__)

#Estableciendo la llave secreta de manera aleatoria
app.secret_key = os.urandom(24)

#Estableciendo la ruta de las imagenes
app.config['UPLOADED_PHOTOS_DEST'] = 'static/image/product'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

#Configurando la conexion con la base de datos
mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'tintoreria_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Inicializando el mysql
mysql.init_app(app)

#Funcion para determinar si ya se esta logeado
def is_logged_in(f):
    @wraps(f)

    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap

#Funcion para determinar si no esta logeado
def not_logged_in(f):
    @wraps(f)

    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap

#Funcion pra determinar si el admin esta logeado
def is_admin_logged_in(f):
    @wraps(f)

    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))

    return wrap

#Funcion pra determinar si el admin no esta logeado
def not_admin_logged_in(f):
    @wraps(f)

    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, *kwargs)

    return wrap

#Funcion para los contenedores
def wrappers(func, *args, **kwargs):

    def wrapped():
        return func(*args, **kwargs)

    return wrapped

#Funcion para mostrar contenido filtrado por la busqueda
def content_based_filtering(product_id):

    #Creando un cursor para la ejecucion
    cur = mysql.connection.cursor()

    #Obteniendo el id del producto y extrayendo sus datos
    cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    data = cur.fetchone()
    data_cat = data['category']  #Obteniendo la categoria del producto buscado

    #Obteniendo todos los productos con la misma categoria
    category_matched = cur.execute("SELECT * FROM products WHERE category=%s", (data_cat,))
    cat_product = cur.fetchall()

    #Obtener la informacion sobre el profucto
    cur.execute("SELECT * FROM product_level WHERE product_id=%s", (product_id,))
    id_level = cur.fetchone()

    recommend_id = []
    cate_level = ['lavado', 'planchado', 'confeccion', 'completo']

    #Recorrer los productos con la misma categoria
    for product_f in cat_product:

        #Obteniendo los productos con el mismo id
        cur.execute("SELECT * FROM product_level WHERE product_id=%s", (product_f['id'],))
        f_level = cur.fetchone()

        match_score = 0

        #Contar los porductos con el mismo id y categoria
        if f_level['product_id'] != int(product_id):
            for cat_level in cate_level:
                if f_level[cat_level] == id_level[cat_level]:
                    match_score += 1

            if match_score >= 2:
                recommend_id.append(f_level['product_id'])

    if recommend_id:
        cur = mysql.connection.cursor()
        placeholders = ','.join((str(n) for n in recommend_id))
        query = 'SELECT * FROM products WHERE id IN (%s)' % placeholders
        cur.execute(query)
        recommend_list = cur.fetchall()
        return recommend_list, recommend_id, category_matched, product_id
    else:
        return ''

#Definiendo la ruta principal
@app.route('/')

#Funcion de la pag principal
def index():

    #Crear un objeto orderform
    form = OrderForm(request.form)

    #Creando un cursor
    cur = mysql.connection.cursor()

    #Creando los mensajes para ejecutar
    values = 'camisa'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    camisas = cur.fetchall()
    values = 'traje'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    trajes = cur.fetchall()
    values = 'pantalon'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    pantalones = cur.fetchall()
    values = 'chemise'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY RAND() LIMIT 4", (values,))
    chemises = cur.fetchall()

    #Cerrar el cursor
    cur.close()

    #Renderizar la pag
    return render_template('home.html', camisas=camisas, trajes=trajes, pantalones=pantalones, chemises=chemises, form=form)

#Creando la clase para el loginform
class LoginForm(Form):

    #Configurando el input
    username = StringField('', [validators.length(min = 1)],
                           render_kw = {'autofocus': True, 'placeholder': 'Usuario'})
    password = PasswordField('', [validators.length(min = 3)],
                             render_kw = {'placeholder': 'Contraseña'})

#Definiendo la ruta para el login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in

#Definiendo la funcion para controlar el login
def login():

    #Creando un objeto de la clase loginform
    form = LoginForm(request.form)

    #Validar que los datos entren correctamente
    if request.method == 'POST' and form.validate():

        #Obtener el usario y Contraseña
        username = form.username.data
        password_candidate = form.password.data

        #Creando un cursor
        cur = mysql.connection.cursor()

        #Obtener un ususario con el nombre ingresado
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            #Obtener informacion sobre el usuario
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['name']

            #Comparar la contraseña incriptada
            if sha256_crypt.verify(password_candidate, password):

                session['logged_in'] = True
                session['uid'] = uid
                session['s_name'] = name
                x = '1'
                cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))

                #Si es correcta regresa el indice
                return redirect(url_for('index'))

            #Clave incorrecta
            else:
                flash('Contraseña incorrecta.', 'danger')
                return render_template('login.html', form = form)

        #Usuario incorrecto
        else:
            flash('El usuario no existe.', 'danger')
            # Close connection
            cur.close()

            #Renderizar la pantalla del login
            return render_template('login.html', form = form)

    #Renderizar la pantalla del login
    return render_template('login.html', form = form)

#Definiendo ruta para deslogearse
@app.route('/out')

#Definiendo la funcion para el deslogeo
def logout():

    if 'uid' in session:

        #Creando un cursor
        cur = mysql.connection.cursor()

        uid = session['uid']
        x = '0'
        cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))
        session.clear()
        flash("Se ha cerrado su sesion.", 'success')

        #Si esta registrado redirigir al indice
        return redirect(url_for('index'))

    #Si no estas logeado redireccionar al login
    return redirect(url_for('login'))

#Creando la clase para el registerform
class RegisterForm(Form):

    #Configurando el input
    name = StringField('', [validators.length(min=3, max = 50)],
                       render_kw = {'autofocus': True, 'placeholder': 'Nombre Completo'})
    username = StringField('', [validators.length(min = 3, max = 25)], render_kw = {'placeholder': 'Nombre de Usuario'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min = 4, max = 50)],
                       render_kw = {'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min = 3)],
                             render_kw = {'placeholder': 'Contraseña'})
    mobile = StringField('', [validators.length(min = 11, max = 15)], render_kw = {'placeholder': 'Telefono'})

#Definiendo la ruta del registro
@app.route('/register', methods=['GET', 'POST'])
@not_logged_in

#Declarando la funcion para el register
def register():

    #Creando un objeto de la clase registerform
    form = RegisterForm(request.form)

    #Validando la entrada correcta de datos
    if request.method == 'POST' and form.validate():

        #Obteniendo los datos
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data)) #Encriptando la contraseña
        mobile = form.mobile.data

        #Creando el cursor y ejecutando la sentencia
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password, mobile) VALUES(%s, %s, %s, %s, %s)",
                    (name, email, username, password, mobile))

        #Haciendo un commit
        mysql.connection.commit()

        #Cerrando el cursor
        cur.close()

        #Mensaje de registro
        flash("Se registro correctamente, ya puedes inicar sesion.", 'success')

        #Redirigiendo al index
        return redirect(url_for('index'))

    #Rendereizando la pantalla del register
    return render_template('register.html', form = form)

#Creando la clase para el orderform
class OrderForm(Form):

    #Configurando el input
    name = StringField('', [validators.length(min=1), validators.DataRequired()],
                       render_kw={'autofocus': True, 'placeholder': 'Nombre completo'})
    mobile_num = StringField('', [validators.length(min=1), validators.DataRequired()],
                             render_kw={'autofocus': True, 'placeholder': 'Telefono'})
    quantity = SelectField('', [validators.DataRequired()],
                           choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    order_place = StringField('', [validators.length(min=1), validators.DataRequired()],
                              render_kw={'placeholder': 'Direccion'})

@app.route('/camisa', methods=['GET', 'POST'])
def camisa():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'camisa'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()

        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('camisa.html', camisas=products, form=form)
    if 'view' in request.args:
        product_id = request.args['view']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        wrappered = wrappers(content_based_filtering, product_id)
        execution_time = timeit.timeit(wrappered, number=0)

        if 'uid' in session:
            uid = session['uid']

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM product_view WHERE user_id=%s AND product_id=%s", (uid, product_id))
            result = cur.fetchall()
            if result:
                now = datetime.datetime.now()
                now_time = now.strftime("%y-%m-%d %H:%M:%S")
                cur.execute("UPDATE product_view SET date=%s WHERE user_id=%s AND product_id=%s",
                            (now_time, uid, product_id))
            else:
                cur.execute("INSERT INTO product_view(user_id, product_id) VALUES(%s, %s)", (uid, product_id))
                mysql.connection.commit()
        return render_template('view_product.html', x=x, producto=product)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('camisa.html', camisas=products, form=form)

@app.route('/franela', methods=['GET', 'POST'])
def franela():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'franela'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']

        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('franela.html', franelas=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('franela.html', franelas=products, form=form)

@app.route('/chemise', methods=['GET', 'POST'])
def chemise():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'chemise'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('chemise.html', chemises=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('chemise.html', chemises=products, form=form)

@app.route('/traje', methods=['GET', 'POST'])
def traje():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'traje'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('traje.html', trajes=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('traje.html', trajes=products, form=form)

@app.route('/corbata', methods=['GET', 'POST'])
def corbata():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'corbata'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('corbata.html', corbatas=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('corbata.html', corbatas=products, form=form)

@app.route('/pantalon', methods=['GET', 'POST'])
def pantalon():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'pantalon'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('pantalon.html', pantalones=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('pantalon.html', pantalones=products, form=form)

@app.route('/sueter', methods=['GET', 'POST'])
def sueter():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'sueter'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('sueter.html', sueteres=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('sueter.html', sueteres=products, form=form)

@app.route('/jean', methods=['GET', 'POST'])
def jean():
    form = OrderForm(request.form)

    cur = mysql.connection.cursor()

    values = 'jean'
    cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,))
    products = cur.fetchall()

    cur.close()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        curs = mysql.connection.cursor()

        curs.execute("SELECT * FROM products WHERE id=%s", (pid,))
        product = curs.fetchall()
        if 'uid' in session:
            uid = session['uid']
            curs.execute("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, product[0]["pName"], mobile, order_place, quantity, now_time))
        else:
            curs.execute("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, product[0]["pName"], mobile, order_place, quantity, now_time))

        mysql.connection.commit()

        cur.close()

        flash('Pedido realizado con exito.', 'success')
        return render_template('jean.html', jeans=products, form=form)
    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (q,))
        products = curso.fetchall()
        return render_template('view_product.html', x=x, producto=products)
    elif 'order' in request.args:
        product_id = request.args['order']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, producto=product, form=form)
    return render_template('jean.html', jeans=products, form=form)

@app.route('/admin_login', methods=['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    if request.method == 'POST':
        # GEt user form
        username = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM admin WHERE email=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['firstName']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['admin_logged_in'] = True
                session['admin_uid'] = uid
                session['admin_name'] = name

                return redirect(url_for('admin'))

            else:
                flash('Contraseña incorrecta.', 'danger')
                return render_template('pages/login.html')

        else:
            flash('El usuario no existe.', 'danger')
            # Close connection
            cur.close()
            return render_template('pages/login.html')
    return render_template('pages/login.html')

@app.route('/admin_out')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin'))

@app.route('/admin')
@is_admin_logged_in
def admin():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    result = curso.fetchall()
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('pages/index.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)

@app.route('/orders')
@is_admin_logged_in
def orders():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    order_rows = curso.execute("SELECT * FROM orders")
    result = curso.fetchall()
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('pages/all_orders.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)

@app.route('/users')
@is_admin_logged_in
def users():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    order_rows = curso.execute("SELECT * FROM orders")
    users_rows = curso.execute("SELECT * FROM users")
    result = curso.fetchall()
    return render_template('pages/all_users.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)

@app.route('/admin_add_product', methods=['POST', 'GET'])
@is_admin_logged_in
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form['price']
        description = request.form['description']
        available = request.form['available']
        category = request.form['category']
        item = request.form['item']
        code = request.form['code']
        file = request.files['picture']
        if name and price and description and available and category and item and code and file:
            pic = file.filename
            photo = pic.replace("'", "")
            picture = photo.replace(" ", "_")
            if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_photo = photos.save(file, folder=category)
                if save_photo:

                    curs = mysql.connection.cursor()
                    curs.execute("INSERT INTO products(pName,price,description,available,category,item,pCode,picture)"
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                                 (name, price, description, available, category, item, code, picture))
                    mysql.connection.commit()
                    product_id = curs.lastrowid
                    curs.execute("INSERT INTO product_level(product_id)" "VALUES(%s)", [product_id])
                    if category == 'camisa':
                        level = request.form.getlist('camisa')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'franela':
                        level = request.form.getlist('franela')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'chemise':
                        level = request.form.getlist('chemise')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'traje':
                        level = request.form.getlist('traje')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'corbata':
                        level = request.form.getlist('corbata')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'pantalon':
                        level = request.form.getlist('pantalon')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'sueter':
                        level = request.form.getlist('sueter')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    elif category == 'jean':
                        level = request.form.getlist('jean')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            curs.execute(query, (yes, product_id))

                            mysql.connection.commit()
                    else:
                        flash('No se ha encontrado la categoria del producto.', 'danger')
                        return redirect(url_for('admin_add_product'))

                    curs.close()

                    flash('Producto agregado correctamente.', 'success')
                    return redirect(url_for('admin_add_product'))
                else:
                    flash('Imagen no guardada.', 'danger')
                    return redirect(url_for('admin_add_product'))
            else:
                flash('Archivo no soportado.', 'danger')
                return redirect(url_for('admin_add_product'))
        else:
            flash('Por favor, rellene todo el formulario.', 'danger')
            return redirect(url_for('admin_add_product'))
    else:
        return render_template('pages/add_product.html')

@app.route('/edit_product', methods=['POST', 'GET'])
@is_admin_logged_in
def edit_product():
    if 'id' in request.args:
        product_id = request.args['id']
        curso = mysql.connection.cursor()
        res = curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        curso.execute("SELECT * FROM product_level WHERE product_id=%s", (product_id,))
        product_level = curso.fetchall()
        if res:
            if request.method == 'POST':
                name = request.form.get('name')
                price = request.form['price']
                description = request.form['description']
                available = request.form['available']
                category = request.form['category']
                item = request.form['item']
                code = request.form['code']
                file = request.files['picture']

                if name and price and description and available and category and item and code and file:
                    pic = file.filename
                    photo = pic.replace("'", "")
                    picture = photo.replace(" ", "")
                    if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file.filename = picture
                        save_photo = photos.save(file, folder=category)
                        if save_photo:

                            cur = mysql.connection.cursor()
                            exe = curso.execute(
                                "UPDATE products SET pName=%s, price=%s, description=%s, available=%s, category=%s, item=%s, pCode=%s, picture=%s WHERE id=%s",
                                (name, price, description, available, category, item, code, picture, product_id))
                            if exe:
                                if category == 'camisa':
                                    level = request.form.getlist('camisa')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'franela':
                                    level = request.form.getlist('franela')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'chemise':
                                    level = request.form.getlist('chemise')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'traje':
                                    level = request.form.getlist('traje')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'corbata':
                                    level = request.form.getlist('corbata')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'pantalon':
                                    level = request.form.getlist('pantalon')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'sueter':
                                    level = request.form.getlist('sueter')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                elif category == 'jean':
                                    level = request.form.getlist('jean')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(
                                            field=lev)
                                        cur.execute(query, (yes, product_id))

                                        mysql.connection.commit()
                                else:
                                    flash('No se encontro la categoria del producto.', 'danger')
                                    return redirect(url_for('admin_add_product'))
                                flash('Producto editado con exito.', 'success')
                                return redirect(url_for('edit_product'))
                            else:
                                flash('Datos editados con exito.', 'success')
                                return redirect(url_for('edit_product'))
                        else:
                            flash('No se pudo actualizar la imagen', 'danger')
                            return render_template('pages/edit_product.html', product=product,
                                                   product_level=product_level)
                    else:
                        flash('Archivo no soportado.', 'danger')
                        return render_template('pages/edit_product.html', product=product,
                                               product_level=product_level)
                else:
                    flash('Por favor, rellene todos los campos.', 'danger')
                    return render_template('pages/edit_product.html', product=product,
                                           product_level=product_level)
            else:
                return render_template('pages/edit_product.html', product=product, product_level=product_level)
        else:
            return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/search', methods=['POST', 'GET'])
def search():
    form = OrderForm(request.form)
    if 'q' in request.args:
        q = request.args['q']

        cur = mysql.connection.cursor()

        query_string = "SELECT * FROM products WHERE pName LIKE %s ORDER BY id ASC"
        cur.execute(query_string, ('%' + q + '%',))
        products = cur.fetchall()

        cur.close()
        flash('Resultados para: ' + q, 'dark')
        return render_template('search.html', products=products, form=form)
    else:
        flash('No se encontro resultados.', 'danger')
        return render_template('search.html')

@app.route('/profile')
@is_logged_in
def profile():
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                curso.execute("SELECT * FROM orders WHERE uid=%s ORDER BY id ASC", (session['uid'],))
                res = curso.fetchall()
                return render_template('profile.html', result=res)
            else:
                flash('No esta autorizado.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('¡No esta autorizado! Ingrese sesion.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('No esta autorizado.', 'danger')
        return redirect(url_for('login'))

class UpdateRegisterForm(Form):
    name = StringField('Nombre Completo', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Nombre Completo'})
    email = EmailField('Correo', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Correo'})
    password = PasswordField('Contraseña', [validators.length(min=3)],
                             render_kw={'placeholder': 'Contraseña'})
    mobile = StringField('Telefono', [validators.length(min=11, max=15)], render_kw={'placeholder': 'Telefono'})

@app.route('/settings', methods=['POST', 'GET'])
@is_logged_in
def settings():
    form = UpdateRegisterForm(request.form)
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                if request.method == 'POST' and form.validate():
                    name = form.name.data
                    email = form.email.data
                    password = sha256_crypt.encrypt(str(form.password.data))
                    mobile = form.mobile.data

                    #Crear el cursor
                    cur = mysql.connection.cursor()
                    exe = cur.execute("UPDATE users SET name=%s, email=%s, password=%s, mobile=%s WHERE id=%s",
                                      (name, email, password, mobile, q))
                    if exe:
                        flash('Datos personales actualizados.', 'success')
                        return render_template('user_settings.html', result=result, form=form)
                    else:
                        flash('Datos no actualizados.', 'danger')
                return render_template('user_settings.html', result=result, form=form)
            else:
                flash('No posee autorizacion.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('¡No posee autorizacion! Ingrese secion.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('No posee autorizacion.', 'danger')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port = 3000, debug=True, use_reloader = False)
