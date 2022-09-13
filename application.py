import io
import os
from os import chdir
from os import getcwd
import json
import pandas as pd
from flask import request, redirect, url_for
from flask import Blueprint, send_file, send_from_directory
from .tests import testCreate, testRun

main = Blueprint('main', __name__)


TABLES = ["PointsFloor", "SquaresFloor", "MaterialsCoef", "Materials", "volume"]


@main.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return (
         """<form action ="" method ="post">
                <input type="text" name="unique"/>
                <input type="submit" name="create"/>
            </form>""" )
    if request.method == 'POST':
        unique = request.form.get('unique')

        for file_name in os.listdir(getcwd() + "/test"):
            # construct full file path
            file = getcwd() + "/test/" + file_name
            if os.path.isfile(file):
                print('Deleting file:', file)
                if file_name != 'RaoBorders.JSON':
                    os.remove(file)
        testCreate.create(unique)

        testRun.tester(unique)
        chdir("./../")
        return (
            """
            <h1>Created</h1>
            <form action ="" method ="post">
                   <input type="text" name="unique"/>
                   <input type="submit" name="create"/>
               </form>""")


@main.route("/type/<int:type>/id/<int:id>")
def show_table(type, id):
    chdir(getcwd() + "/test")
    if type in range(4):
        try:
            x = json.load(open(TABLES[type] + "_number_" + str(id) + '.JSON'))
        except:
            x = "Not Found"
    elif type == 4:
        try:
            x = pd.read_excel(TABLES[type] + "_" + str(id) + '.xlsx').to_dict('records')
        except:
            x = "Not Found"
    else:
        x = "Not Found"
    chdir("./../")
    return x

@main.route('/clear')
def clear():
    for file_name in os.listdir(getcwd() + "/test"):
        file = getcwd() + "/test/" + file_name
        if os.path.isfile(file):
            print('Deleting file:', file)
            if file_name != 'RaoBorders.JSON':
                os.remove(file)
    return redirect(url_for('main.index'))

@main.route('/get/type/<int:type>/id/<int:id>')
def get_file(type,id):
    if type in range(4):
        try:
            filename = TABLES[type] + "_number_" + str(id) + '.JSON'
            return send_from_directory(getcwd() + "/test", filename, as_attachment=True)
        except:
            x = "Not Found"
    elif type == 4:
        try:
            filename = TABLES[type] + "_" + str(id) + '.xlsx'
            return send_from_directory(getcwd() + "/test" ,filename, as_attachment=True)
        except:
            x = "Not Found"
    else:
        x = "Not Found"
    return x
