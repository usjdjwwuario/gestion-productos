from app import app
from flask import Flask, render_template, request, jsonify
import pymongo
from bson.json_util import dumps
import os
from app import app, conexion, db, categorias, productos, usuarios
from werkzeug.utils import secure_filename


@app.route("/obtenerCategorias")
def obtenerCategorias():
    listaCategorias = categorias.find()
    return render_template("listarProductos.html",
                           categorias=listaCategorias)

