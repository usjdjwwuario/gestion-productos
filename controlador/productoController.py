import os
from bson.objectid import ObjectId
import pymongo
from PIL import Image
from io import BytesIO
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from app import app
from baseDATOS.mongodb import productos, categorias


@app.route("/mostrarProductos", methods=['GET', 'POST'])
def mostrarProductos():
    if 'usuario' in session:
        listaProductos = productos.find()
        listaCategorias = categorias.find()
        listaP = []
        for p in listaProductos:
            categoria = categorias.find_one({'_id': p['categoria']})
            if categoria:
                p['categoria'] = categoria['nombre']
            else:
                p['categoria'] = "Sin categoría"
            listaP.append(p)
        return render_template("listaProductos.html", productos=listaP, listaCategorias=listaCategorias)
    else:
        return redirect(url_for('login'))  # Redirigir al formulario de inicio de sesión si el usuario no está autenticado
    
@app.route('/vistaAgregarProducto', methods=['GET'])
def vistaAgregarProducto():
    categorias_from_db = categorias.find()
    return render_template('Form.html', categorias=categorias_from_db)

@app.route('/agregarProducto', methods=['POST'])
def agregarProducto():
    mensaje = None
    estado = False
    try:
        codigo = int(request.form['codigo'])
        nombre = request.form['nombre']
        precio = int(request.form['precio'])
        idCategoria = ObjectId(request.form['cdCategoria'])
        foto = request.files['fileFoto'] 
        producto = {
            'codigo': codigo,
            'nombre': nombre,
            'precio': precio,
            'categoria': idCategoria
        }
        resultado = productos.insert_one(producto)
        if (resultado.acknowledged):
            idProducto = resultado.inserted_id
            nombreFotos = f'{idProducto}.jpg'
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombreFotos))
            mensaje = 'Producto Agregado Correctamente'
            estado = True
        else:
            mensaje = 'Problema Al Agregar El Producto'
    except pymongo.errors.PyMongoError as error:  
        mensaje = str(error)
        flash((mensaje, estado))  # Usar flash para pasar el mensaje y el estado a la página siguiente
    return redirect(url_for('listaProductos'))



def consultarProducto(codigo):
    try:
        consulta = {"codigo": codigo}
        producto = productos.find_one(consulta)
        if (producto is not None):
            return True
        else:
            return False
    except pymongo.error as error:
        print(error)
        return False


@app.route('/agregarProductoJson', methods=['POST'])
def agregarProductoJson():
    estado = False
    mensaje = None
    try:
        datos = request.json
        producto = datos.get('producto')
        fotoBase64 = datos.get('foto')["foto"]
        producto = {
            'codigo': int(producto["codigo"]),
            'nombre': producto["nombre"],
            'precio': int(producto["precio"]),
            'categoria': ObjectId(producto["categoria"])
        }
        resultado = productos.insert_one(producto)
        if resultado.acknowledged:
            rutaImagen = f"{os.path.join(app.config['UPLOAD_FOLDER'])}/{resultado.inserted_id}.jpg"
            fotoBase64 = fotoBase64[fotoBase64.index(',') + 1]
            fotoDecodificada = base64.b64decode(fotoBase64)
            imagen = Image.open(BytesIO(fotoDecodificada))
            imagenJpg = imagen.convert('RGB')
            imagen.save(rutaImagen)
            estado = True
            mensaje = 'Producto Agregado'
        else:
            mensaje = 'Problemas al Agregar'
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    retorno = {"estado": estado, "mensaje": mensaje}
    return jsonify(retorno)


@app.route("/consultar/<codigo>", methods= ["GET"])
def consultar(codigo):
    if ("user" in session):
        #se hace para una consulta
        producto = producto.objects(codigo=codigo).first()
        listaCategorias = categorias.objects()
        return render_template("editar.html", producto=producto, categorias=listaCategorias)
    else:
        mensaje="Debe de primero de ingresar sus credenciales"
        return render_template("login.html", mensaje=mensaje)


@app.route("/consultar/<codigo>", methods=["GET"])
def consultarPorCodigo(codigo):
    estado=False
    mensaje=None
    producto=None

    try:
        datosConsulta={'codigo':int(codigo)}
        producto=producto.find_one(datosConsulta)
        if (producto):
            estado=True
    except pymongo.errors as error:
        mensaje=error
    listaCategorias = categorias.find()
    return render_template("formEditar.html", producto=producto, categorias=listaCategorias)


@app.route("/editar", methods=["POST"])
def editar():
    estado=False
    mensaje=None
    try:
        codigo = int(request.form['codigo'])
        nombre = request.form['nombre']
        precio = int(request.form['precio'])
        idCategoria = ObjectId(request.form['cdCategoria'])
        foto = request.files['fileFoto'] 
        idProducto=request.form['idProducto']
        producto = {
            'codigo': codigo,
            'nombre': nombre,
            'precio': precio,
            'categoria': idCategoria
        }

        resultado = productos.update_one({'_id':idProducto},{"$set": producto})
        #acknowledged que indica si el servidor de MongoDB confirmó que recibió y procesó la operación de escritura.
        if (resultado.acknowledged):
            listaCategorias = categorias.find()

            if(foto):
                nombreFoto=f"{idProducto}.jpg"
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombreFoto))
            mensaje="actualizado"
        else:
            mensaje="problemas al actualizar"

    except pymongo.errors as error:
        mensaje=error
    return render_template("formEditar.html", producto=producto, categorias=listaCategorias)