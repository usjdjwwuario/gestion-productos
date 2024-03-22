import os
from bson.objectid import ObjectId
import pymongo
from PIL import Image
from io import BytesIO
import base64
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from app import app, conexion, db, categorias, productos, usuarios



@app.route("/mostrarProductos", methods=['GET'])
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
        return render_template("frmIniciarSeccion.html") 
    
@app.route('/vistaAgregarProducto', methods=['GET'])
def vistaAgregarProducto():
    categorias_from_db = categorias.find()
    return render_template('listarProductos.html', categorias=categorias_from_db)

@app.route('/agregarProducto1', methods=['POST'])
def agregarProducto1():
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
        flash((mensaje, estado)) 
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


@app.route('/agregarProducto', methods=['POST'])
def agregarProducto():
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
    return render_template("editar.html", producto=producto, categorias=listaCategorias)


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
    return render_template("editar.html", producto=producto, categorias=listaCategorias)