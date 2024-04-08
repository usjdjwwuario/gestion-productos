from app import app
from flask import Flask, render_template, request, redirect, session,url_for
import pymongo
from app import app, conexion, db, categorias, productos, usuarios
@app.route("/")
def visitaIniciarSeccion():
    return render_template("frmIniciarSeccion.html")

@app.route("/", methods=["POST"])
def iniciarSesion():
    mensaje=None
    estado=None
    try:
        correo  = request.form["correo"]
        contraseña = request.form["contraseña"]
        consulta = {"correo":correo, "contraseña":contraseña}
        user = usuarios.find_one(consulta)
        if user:
            session["correo"]=correo
            return redirect (url_for("mostrarProdutos"))
        else:
            mensaje = "Datos no validos"   
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    print("Error de MongoDB:", mensaje)
    
    return render_template("frmIniciarSeccion.html",estado=estado,mensaje=mensaje)