from random import seed
from random import randint as rand
from random import uniform as randf
from random import choice
from os import mkdir
from os import chdir
from os import getcwd
from os import remove
import json
import pandas as pd
from pathlib import Path
from math import isnan
from flask import Flask
from flask import request, escape,  redirect


app = Flask(__name__)




MATERIALS = ["concrete", "plastic", "steel_mark_1", "steel_mark_2", "aluminum"]

TABLES = ["PointsFloor", "SquaresFloor", "MaterialsCoef", "Materials", "Volume"]

matc = []  # this was made to account for same material names for same id

def fillTable(i, table="PointsFloor"):
    """
    Generates a single row of a table with integer id 'i'

    also requires 'table' argument, which takes string values:
    PointsFloor
    SquaresFloor
    MaterialsCoef
    Materials

    Always returns a dictionary of type 'row_name':value
    """
    global matc
    if len(matc) < i:
        matc.append(rand(0, 4))

    if table == "PointsFloor":
        return {"id": i,
                "room_name": str(rand(1, 7)),
                "material": MATERIALS[matc[i - 1]],
                "alpha_UA": None,
                "beta_UA": None,
                "alpha_F": None,
                "beta_F": rand(1, 1000),
                "gamma_EP": None,
                "quantity": rand(1, 100),
                "files_id": 82}
    elif table == "SquaresFloor":
        return {"id": i,
                "room_name": str(rand(1, 4)),
                "material": MATERIALS[matc[i - 1]],
                "square": "{:.2f}".format(randf(1, 100)),
                "files_id": 82}
    elif table == "MaterialsCoef":
        maxc = float("{:.2f}".format(randf(0.1, 1)))
        minc = float("{:.2f}".format(randf(0.1, maxc)))
        return {"id": i,
                "materials_id": matc[i - 1],
                "files_id": 82,
                "width": "{:.2f}".format(randf(1, 100)),
                "coef_tie": "{:.2f}".format(randf(minc, maxc)),
                "coef_tie_min": minc,
                "coef_tie_max": maxc,
                "coef_tie_sko": "{:.2f}".format(randf(minc, maxc)),
                "coef_tie_distrib": str(rand(1, 7)),
                "deactivation_methods_id": int(i * maxc + 1)}  # some messing with generation here
    elif table == "Materials":
        maxc = [float("{:.2f}".format(randf(0.1, 1))) for x in range(6)]
        minc = [float("{:.2f}".format(randf(0.1, maxc[x]))) for x in range(6)]
        metd = lambda x: 0 if x <= 1 else 1
        return {"id": i,
                "name": MATERIALS[matc[i - 1]],
                "list_subname": choice(["C0", "C1", "B1", "B2", "D"]),
                "files_id": 82,
                "coef_transition": "{:.2f}".format(randf(minc[0], maxc[0])),
                "coef_transition_min": minc[0],
                "coef_transition_max": maxc[0],
                "coef_transition_sko": "{:.2f}".format(randf(minc[0], maxc[0])),
                "coef_transition_distrib": str(rand(1, 7)),
                "density": "{:.2f}".format(randf(minc[1], maxc[1])),
                "density_min": minc[1],
                "density_max": maxc[1],
                "density_sko": "{:.2f}".format(randf(minc[1], maxc[1])),
                "density_distrib": str(rand(1, 7)),
                "coef_density_change": "{:.2f}".format(randf(0, 1)),
                "coef_density_change_sko": "{:.2f}".format(randf(0, 1)),
                "metal": metd(matc[i - 1]),
                "key_words_fer_id": rand(0, 1),
                "smooth": rand(0, 1),
                "alpha_kiro_min": minc[2],
                "alpha_kiro": "{:.2f}".format(randf(minc[2], maxc[2])),
                "alpha_kiro_max": maxc[2],
                "beta_kiro_min": minc[4],
                "beta_kiro": "{:.2f}".format(randf(minc[3], maxc[3])),
                "beta_kiro_max": maxc[3],
                "alpha_coef_floor_wall_min": minc[4],
                "alpha_coef_floor_wall": "{:.2f}".format(randf(minc[4], maxc[4])),
                "alpha_coef_floor_wall_max": maxc[4],
                "beta_coef_floor_wall_min": minc[5],
                "beta_coef_floor_wall_kiro": "{:.2f}".format(randf(minc[5], maxc[5])),
                "beta_coef_floor_wall_max": maxc[5]}


def tableFiller(table_list=None, foo=fillTable, times=False,
                **kwargs):
    """
    Creates tables, using custom function for row generation.
    In this case, fillTable by default.

    Takes list of tables' names that should be specified in row generating function,
    the generating function and how many rows should there be in each table.
    It also takes additional arguments for generating function, if needed.

    Returns a dictionary of type 'table_name':table.

    P.S. I could have used yield to make fillTable a generator instead,
    but then I would fail to generate tables that match by id, materials and etc.
    Also had some thoughts about reusing this later, but I never did.
    """
    if table_list is None:
        table_list = ["PointsFloor", "SquaresFloor", "MaterialsCoef", "Materials"]
    table_of_tables = {}
    for i in table_list:
        table = []
        if times:
            for j in range(1, times + 1):
                table.append(foo(j, i, **kwargs))
        else:
            table.append(foo(i, **kwargs))
        table_of_tables[i] = table
    return table_of_tables


def createTable(table, tablename="table", xlsx=False, keepJSON=False):
    """
    Creates files for tables, either xlsx, JSON or both.

    P.S. It creates both files and rewrites a JSON anyway, due to
    default json.dumps method being unable to read nan as np.nan,
    instead reading it as string 'nan'. This was way too problematic and
    there was no built-in solution, so I decided to leave it as is — now it
    works slightly slower, but it works.
    """
    with open(tablename + ".JSON", "w") as f:
        f.write(json.dumps(table, allow_nan=True))
    table = pd.read_json(tablename + ".JSON")
    table.to_excel(tablename + ".xlsx", index=False)
    with open(tablename + ".JSON", "w") as f:
        f.write(json.dumps(pd.read_excel(tablename + '.xlsx').to_dict('records')))
    if not xlsx:
        keepJSON = True
        remove(tablename + ".xlsx")
    if not keepJSON:
        remove(tablename + ".JSON")


def jsonRead(table, parsed=True, func=pd.DataFrame, i=0):
    """
    Simple function that reads json files,
    made just to navigate through different names
    that were used during testing etc.

    Takes table name, a bool variable that indicates
    whether the file has 'parsed' prefix a number 'i'
    that indicates the unique id of instance of a table
    and a function that determines how to save the read JSON.

    Returns object of a type that 'func' converts the table to.
    """
    if parsed:
        return func(json.load(open("parsed" + table + '.JSON')))
    else:
        if not i:
            return func(json.load(open(table + '.JSON')))
        else:
            return func(json.load(open(table + '_number_' + str(i) + '.JSON')))


def getAllUA(alpha_F=0, beta_F=0, alpha_kiro=1, beta_kiro=1):
    """
    This function calculates the value of AllUA variable.
    It also takes care of missing values, if there are any.
    The input is self-explanatory.
    Returns a float value cut by 2 decimal digits.
    """
    check = lambda x: 0 if (isnan(x) or x == None) else x
    return float(f'{(check(alpha_F) / check(alpha_kiro) + check(beta_F) / check(beta_kiro)):.2f}')


def defineRaoType(UA, rao, metal):
    """
    Returns rao type depending on whether material is metal and
    whether it passes the threshold for certain rao type

    returns string that specifies rao type
    """
    rao = rao.set_index(['material'])
    if metal:
        for i in rao:
            if UA <= rao.at["Metal", i]:
                return i
    else:
        for i in rao:
            if UA <= rao.at["Not Metal", i]:
                return i

def create(times = 10, number = 4, cwd = getcwd(), seed = 111):
    '''
    creates standart randomly generated tables.
    :param times: rows in a table
    :param number: number of tables
    :param cwd: directory where tables will be saved
    :param seed: seeds the table generation
    :return: exit code
    '''
    #Path(cwd + "/test").mkdir(parents=True, exist_ok=True)
    chdir(cwd)
    for i in range(1,number+1):
        table_of_tables = tableFiller(table_list=["PointsFloor", "SquaresFloor", "MaterialsCoef", "Materials"], times = times)
        for j in table_of_tables:
            createTable(table = table_of_tables[j], tablename = (j +"_number_"+ str(i)))
    return 0

def createVolume(number = 0, cwd_test = getcwd(), cwd_target = getcwd()):
    '''
    creates volume table that is a modified version of floor table
    :param number: id of the volume table
    :param cwd_test: directory from where all the source tables are taken
    :param cwd_target: directory where the volume table with corresponding id will be made
    :return: exit code
    '''

    #   there tables are read and volume dataframe is created
    rao = jsonRead("RaoBorders", parsed=False)
    chdir(cwd_test)
    floor = jsonRead("PointsFloor", parsed=False, i=number)
    square = jsonRead("SquaresFloor", parsed=False, i=number)
    mat = jsonRead("Materials", parsed=False, i=number)
    matcoef = jsonRead("MaterialsCoef", parsed=False, i=number)
    volume = floor[floor["room_name"].isin(square["room_name"].unique())]
    volume = volume.reset_index()
    volume = volume.drop(columns=["index"])
    print("Correctness of Volume dataframe creation:",
          square["room_name"].unique().sort() == volume["room_name"].unique().sort())

    #   all_UA variable is added to volume dataframe here
    all_UA = []
    for i in range(min(len(volume['alpha_F']), len(volume['beta_F']))):
        all_UA.append(
            getAllUA(volume.at[i, 'alpha_F'], volume.at[i, 'beta_F'], mat.at[i, 'alpha_kiro'], mat.at[i, 'beta_kiro']))
    volume = volume.assign(all_UA=pd.Series(all_UA))

    #   further calculatuons are made according to 'after' variable value
    print("Input value of variable `after`: ", end='')
    after = int(input())
    if after:
        placeholder = 2  # because needed coefficient was not provided
        volume['all_UA'] = (volume['all_UA'] / placeholder).round(2)

    #   adds a column to volume that determines which rao type the observation belongs to
    rao_UA = []
    for i in range(len(volume['all_UA'])):
        rao_UA.append(defineRaoType(volume.loc[i, 'all_UA'], rao, mat.loc[i, 'metal']))
    volume = volume.assign(RAO=pd.Series(rao_UA))

    #   counts quantity by room and material type and converts it to new tables that appends
    volume_aggmat = volume.groupby(by=['room_name', 'material']).sum()['quantity']
    volume_aggrao = volume.groupby(by=['room_name', 'material', 'RAO']).sum()['quantity']
    volume_aggrao_concat = pd.pivot_table(pd.DataFrame(volume_aggrao), index=['room_name', 'material'], columns=['RAO'],
                                          values=['quantity'])
    volume_aggmat_concat = pd.pivot_table(pd.DataFrame(volume_aggmat), index=['room_name', 'material'],
                                          values=['quantity'])
    volume = volume.merge(volume_aggrao_concat, how='left', on=['room_name', 'material'])

    #   this part fixes broken naming that was automatically done by
    #   combination of group_by and pivot_table.
    names = []
    for name in volume.columns:
        if name not in ["id", "room_name", "material", "alpha_UA", "beta_UA", "alpha_F", "beta_F", "gamma_EP",
                        "quantity", "files_id", "all_UA", "RAO"]:
            names.append(str(name).lstrip("(\'quantity\',").strip("\'() \'"))
        else:
            names.append(name)
    volume.columns = names

    #   finds proportion of rao type in the room to all rao in same room
    volume = volume.merge(volume_aggmat_concat, how='left', on=['room_name', 'material'])
    for col in volume["RAO"].unique():
        volume[col + "_part"] = volume[col] / volume['quantity_y']

    #   does other interim calculations that result in tempCoef column
    volume = volume.merge(pd.DataFrame({"id": mat.loc[mat["id"].isin(volume["id"])]["id"],
                                        "coefLoosening": 1 / mat.loc[mat["id"].isin(volume["id"])][
                                            'coef_density_change']}), how="left", on=["id"])
    square['square*width'] = square['square'] * matcoef['width']
    volume = volume.merge(square[['id', 'square*width']], on='id', how='left')
    volume['tempCoef'] = volume['coefLoosening'] * volume['square*width']

    #   final calculations for each rao type
    for col in volume["RAO"].unique():
        volume[col + "_part*tempCoef"] = volume[col + "_part"] * volume['tempCoef']

    #   creates final volume table
    chdir(cwd_target)
    createTable(volume.to_dict('records'), "Volume_" + str(number), xlsx=True)
    return 0



@app.route("/")
def index():
    unique = request.args.get("unique")
    for i in range(1, int(unique) + 1):
        create(i)
        createVolume(i)
    return (
            """<form action ="" method ="get">
                    <input type="text" name="number of unique tables"/>
                    <input type="submit" name="create"/> 
                </form>"""
            + unique
    )

@app.route("/<int:type>/<int:id>")
def show_table(type, id):
    return pd.read_excel(TABLES[type] + "_" + str(id) + '.xlsx').to_dict('records')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)