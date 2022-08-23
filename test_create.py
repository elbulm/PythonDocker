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


MATERIALS = ["concrete", "plastic", "steel_mark_1", "steel_mark_2", "aluminum"]

matc = []

def fillTable(i, table = "PointsFloor"):
    global matc
    if len(matc) < i:
        matc.append(rand(0, 4))

    if table == "PointsFloor":
        return {"id": i,
                "room_name": str(rand(1, 7)),
                "material": MATERIALS[matc[i-1]],
                "alpha_UA": None,
                "beta_UA": None,
                "alpha_F": None,
                "beta_F": rand(1,1000),
                "gamma_EP": None,
                "quantity": rand(1,100),
                "files_id": 82}
    elif table == "SquaresFloor":
        return {"id": i,
                "room_name": str(rand(1,4)),
                "material": MATERIALS[matc[i-1]],
                "square": "{:.2f}".format(randf(1, 100)),
                "files_id": 82}
    elif table == "MaterialsCoef":
        maxc = float("{:.2f}".format(randf(0.1, 1)))
        minc = float("{:.2f}".format(randf(0.1, maxc)))
        return {"id": i,
                "materials_id": matc[i-1],
                "files_id": 82,
                "width": "{:.2f}".format(randf(1,100)),
                "coef_tie": "{:.2f}".format(randf(minc, maxc)),
                "coef_tie_min": minc,
                "coef_tie_max": maxc,
                "coef_tie_sko": "{:.2f}".format(randf(minc, maxc)),
                "coef_tie_distrib": str(rand(1,7)),
                "deactivation_methods_id": int(i*maxc +1)} #some messing with generation here
    elif table == "Materials":
        maxc = [float("{:.2f}".format(randf(0.1,1))) for x in range(6)]
        minc = [float("{:.2f}".format(randf(0.1,maxc[x]))) for x in range(6)]
        metd = lambda x: 0 if x <=1 else 1
        return {"id" : i,
                "name": MATERIALS[matc[i-1]],
                "list_subname": choice(["C0", "C1", "B1", "B2", "D"]),
                "files_id": 82,
                "coef_transition": "{:.2f}".format(randf(minc[0], maxc[0])),
                "coef_transition_min" : minc[0],
                "coef_transition_max": maxc[0],
                "coef_transition_sko": "{:.2f}".format(randf(minc[0], maxc[0])),
                "coef_transition_distrib" : str(rand(1,7)),
                "density": "{:.2f}".format(randf(minc[1], maxc[1])),
                "density_min" : minc[1],
                "density_max": maxc[1],
                "density_sko": "{:.2f}".format(randf(minc[1], maxc[1])),
                "density_distrib" : str(rand(1,7)),
                "coef_density_change": "{:.2f}".format(randf(0, 1)),
                "coef_density_change_sko":  "{:.2f}".format(randf(0, 1)),
                "metal": metd(matc[i-1]),
                "key_words_fer_id": rand(0,1),
                "smooth": rand(0,1),
                "alpha_kiro_min": minc[2],
                "alpha_kiro" : "{:.2f}".format(randf(minc[2], maxc[2])),
                "alpha_kiro_max": maxc[2],
                "beta_kiro_min": minc[4],
                "beta_kiro" : "{:.2f}".format(randf(minc[3], maxc[3])),
                "beta_kiro_max": maxc[3],
                "alpha_coef_floor_wall_min": minc[4],
                "alpha_coef_floor_wall" : "{:.2f}".format(randf(minc[4], maxc[4])),
                "alpha_coef_floor_wall_max": maxc[4],
                "beta_coef_floor_wall_min": minc[5],
                "beta_coef_floor_wall_kiro" : "{:.2f}".format(randf(minc[5], maxc[5])),
                "beta_coef_floor_wall_max": maxc[5]}

def tableIterator(table_list = ["PointsFloor", "SquaresFloor", "MaterialsCoef", "Materials"], foo = fillTable, times = False, tableNum = False, **kwargs):
    table_of_tables = {}
    if ~tableNum:
        for i in table_list:
            table = []
            if times:
                for j in range(1, times+1):
                    table.append(foo(j,i,**kwargs))
            else:
                table.append(foo(i, **kwargs))
            table_of_tables[i] = table
    else:
        for i in table_list[tableNum]:
            table = []
            if times:
                for j in range(1, times+1):
                    table.append(foo(j,i,**kwargs))
            else:
                table.append(foo(i, **kwargs))
            table_of_tables[i] = table
    return table_of_tables
        
def createTable(table, tablename = "table", xlsx = False, keepJSON = False):
    with open(tablename +".JSON","w") as f:
        f.write(json.dumps(table, allow_nan = True))
    table = pd.read_json(tablename+".JSON")
    table.to_excel(tablename+".xlsx", index = False)
    with open(tablename + ".JSON","w") as f:
        f.write(json.dumps(pd.read_excel(tablename + '.xlsx').to_dict('records'))) #otherwise nans will be read as strings for some reason and everything breaks lol
    if not xlsx:
        keepJSON = True
        remove(tablename +".xlsx")
    if not keepJSON:
        remove(tablename +".JSON")
        



def main():
    print("How many unique copies of tables do you need?")
    number = int(input())
    seed(111)
    cwd = getcwd()
    Path(cwd + "/test").mkdir(parents=True, exist_ok=True)
    chdir(cwd + "/test/")
    for i in range(1,number+1):
        table_of_tables = tableIterator(times = 10)
        for j in table_of_tables:
            createTable(table = table_of_tables[j], tablename = (j +"_number_"+ str(i)))
    return 0
    
main()
