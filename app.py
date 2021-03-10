from flask import Flask, render_template, request, url_for, redirect, session, g, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

#Connection
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'boleta'
app.config['MYSQL_PORT'] = 3310
mysql = MySQL(app)


#Settings

app.secret_key = 'mysecretkey'


# PAGINA PRINCIPAL

@app.route('/', methods=['GET', 'POST'])
def home():

    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
    else:
        g.user = None
        g.id = None

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        categoria = request.form['categoria']
        busqueda = request.form['search']
        print(busqueda)
        if busqueda != "":
            cur.execute('SELECT e.*, YEAR(es.fecha), MONTHNAME(es.fecha), DAY(es.fecha) FROM evento e, evento_show es WHERE  e.id_evento = es.id_evento AND e.nombre LIKE UPPER(%s)',(busqueda+"%",))
            data = cur.fetchall()
            return render_template('index.html', eventos = data, user = g.user)
        else:
            if categoria != 'todas':
                cur.execute('SELECT e.*, YEAR(es.fecha), MONTHNAME(es.fecha), DAY(es.fecha) FROM evento e, evento_show es WHERE  e.id_evento = es.id_evento AND e.catergoria = %s',(categoria,))
                data = cur.fetchall()
                return render_template('index.html', eventos = data, user = g.user)
            else:
                cur.execute('SELECT e.*, YEAR(es.fecha), MONTHNAME(es.fecha), DAY(es.fecha) FROM evento e, evento_show es WHERE  e.id_evento = es.id_evento')
                data = cur.fetchall()
                return render_template('index.html', eventos = data, user = g.user)
    
    cur.execute('SELECT e.*, YEAR(es.fecha), MONTHNAME(es.fecha), DAY(es.fecha) FROM evento e, evento_show es WHERE  e.id_evento = es.id_evento')
    data = cur.fetchall()
    return render_template('index.html', eventos = data, user = g.user)


# USUARIOS

@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuario WHERE email =  %s", (email,))
            rows = cur.fetchall()
            data = rows[0]
            if check_password_hash(data[1], password):
                session['username'] = [data[0], data[2], 'usuario']
                return redirect(url_for('home'))
            else:
                flash('Credenciales Incorrectas')
                return redirect(url_for('signin'))
            
        except:
            flash('Correo No Registrado')
            return redirect(url_for('signin'))
  
    return render_template('signin.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup_add', methods=['POST'])
def add_user():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='sha256')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE email = %s ', (email,))
        rows = cur.fetchall()
        if rows:
            flash('Correo Registrado')
            return redirect(url_for('signup'))
        else:
            cur.execute("INSERT INTO usuario (nombre, apellido, email, password) VALUES (%s,%s,%s,%s)", (nombre, apellido, email, password))
            mysql.connection.commit()
            flash('Usuario registrado exitosamente')
            return redirect(url_for('signin'))


# ENTIDAD ORGANIZADORA

@app.route('/add_entidad', methods=['GET', 'POST'])
def add_entidad():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='sha256')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM entidad_organizadora WHERE correo = %s ', (email,))
        rows = cur.fetchall()
        if rows:
            flash('Correo Registrado')
            return redirect(url_for('signin_entidad'))
        else:
            cur.execute("INSERT INTO entidad_organizadora (nombre, direccion, telefono, correo, password) VALUES (%s,%s,%s,%s,%s)", (nombre, direccion, telefono, email, password))
            mysql.connection.commit()
            flash('Entidad registrada exitosamente')
            return redirect(url_for('signin_entidad'))

    return render_template('add_entidad.html')

@app.route('/signin_entidad', methods=['GET', 'POST'])
def signin_entidad():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM entidad_organizadora WHERE correo =  %s", (email,))
        rows = cur.fetchall()
        data = rows[0]
        if data:
            if check_password_hash(data[5], password):
                session['username'] = [data[0], data[1], 'entidad']
                return redirect(url_for('entidad'))
            else:
                flash('Credenciales Incorrectas')
                return redirect(url_for('signin_entidad'))
        else:
            flash('Entidad no Registrada')
            return redirect(url_for('add_entidad'))
    return render_template('signin_entidad.html')

@app.route('/entidad')
def entidad():
    cur = mysql.connection.cursor()
    if 'username' in session:
        if session['username'][2] == 'entidad':
            g.user = session['username'][1]
            g.id = session['username'][0]
            cur.execute('SELECT e.*, es.fecha FROM evento e, evento_show es WHERE responsable = %s AND e.id_evento=es.id_evento',(g.id,))
            data = cur.fetchall()
            return render_template('entidad_evento.html', eventos=data ,user=g.user)
        else:
            return redirect(url_for('home'))
    else:
        g.user = None
        g.id = None
        return redirect(url_for('home'))


# VISTA DE EVENTOS


@app.route('/vista_evento/<id_event>')
def vista_event(id_event):
    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
    else:
        g.user = None
        g.id = None
    cur = mysql.connection.cursor()
    cur.execute("""select e.nombre, e.img_evento, e.catergoria, e.lim_edad, e.descripcion, es.fecha, es.ciudad, es.direccion, o.nombre, a.nombre, es.hora, a.id_auditorio, e.id_evento from evento e, evento_show es, entidad_organizadora o, auditorio a
        where e.id_evento = es.id_evento
        and e.responsable = o.id_entidad
        and a.id_auditorio = es.id_auditorio
        and e.id_evento = %s""",(id_event,))
    g.view = cur.fetchall()[0]
    print(g.view)
    cur.execute('SELECT * FROM clase_asiento where id_auditorio = %s', (g.view[11],))
    clase_asiento = cur.fetchall()
    print(clase_asiento)
    return render_template('vista_evento.html', evento=g.view, clases_asiento=clase_asiento, user = g.user)

@app.route('/compra/<id_clase>/<id_evento>')
def compra(id_clase, id_evento):
    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
    else:
        g.user = None
        g.id = None
        return redirect(url_for('signin'))
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clase_asiento WHERE id_claseasiento = %s',(id_clase,))
    row = cur.fetchall()[0]
    cur.execute('SELECT * FROM forma_pago')
    forma_pago = cur.fetchall()
    return render_template('compra.html', clase = row, user=g.user, formas_pago=forma_pago, evento=id_evento)


# EVENTOS

@app.route('/add_evento', methods=['GET', 'POST'])
def add_evento():
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        limEdad = request.form['limEdad']
        descripcion = request.form['descripcion']
        imagen = request.files['img']
        imgname = imagen.filename
        imagen.save(os.path.join('./static/img/', imgname))
        g.id = session['username'][0]
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO evento (nombre, img_evento, catergoria, lim_edad, descripcion, responsable) VALUES (%s,%s,%s,%s,%s,%s)',(nombre,imgname, categoria, limEdad, descripcion, g.id))
        mysql.connection.commit()
        cur.execute('SELECT id_evento FROM evento WHERE nombre=%s',(nombre,))
        id_event = cur.fetchall()[0]
        ciudad = request.form['ciudad']
        fecha = request.form['fecha']
        hora = request.form['hora']
        direccion = request.form['direccion']
        auditorio = request.form['auditorio']
        cur.execute('INSERT INTO evento_show (fecha, ciudad, id_auditorio, id_evento, hora, direccion) VALUES (%s,%s,%s,%s,%s,%s)',(fecha, ciudad, auditorio, id_event,hora,direccion))
        mysql.connection.commit()
        return redirect(url_for('entidad'))
    else:
        if 'username' in session:
            g.user = session['username'][1]
            g.id = session['username'][0]
            if session['username'][2] == 'entidad':
                return render_template('add_evento.html', user = g.user)
            else:
                return redirect(url_for('home'))
        else:
            g.user = None
            g.id = None
            return redirect(url_for('home'))

@app.route('/resumen_boleta/<id_evento>')
def boleta(id_evento):
    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
    else:
        g.user = None
        g.id = None
        return redirect(url_for('signin'))
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre FROM evento WHERE id_evento=%s',(id_evento,))
    nombre = cur.fetchall()[0]
    cantidad = request.args.get("cantidad")
    costo = request.args.get("total")
    clase = request.args.get("clase_asiento")
    forma_pago = request.args.get("forma_pago")
    data = [cantidad, costo, clase, forma_pago, nombre]
    return render_template('boleta.html', data = data, user=g.user)

@app.route('/compraFinal')
def compraFinal():
    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
    else:
        g.user = None
        g.id = None
        return redirect(url_for('signin'))
    precio = request.args.get('costo')
    cantidad = request.args.get('cantidad')
    forma = request.args.get('pago')
    cur = mysql.connection.cursor()
    cur.execute('SELECT id_forma_pago FROM forma_pago WHERE forma_pago = %s',(forma,))
    id_forma = cur.fetchall()[0][0]
    cur.execute('INSERT INTO compra (precio, cantidad_boleta, id_usuario, forma_pago) VALUES (%s, %s, %s, %s)',(precio, cantidad, g.id, id_forma))
    mysql.connection.commit()
    return render_template('final_compra.html', user=g.user)


@app.route('/profile')
def profile():
    if 'username' in session:
        g.user = session['username'][1]
        g.id = session['username'][0]
        if session['username'][2] == 'entidad':
            return redirect(url_for('entidad'))
        else:
            return redirect(url_for('home'))
    else:
        g.user = None
        g.id = None
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)