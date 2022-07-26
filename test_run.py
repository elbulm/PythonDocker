import pandas as pd
import json
from math import isnan
from os import remove
from os import mkdir
from os import chdir
from os import getcwd




def jsonRead(table, parsed = True, func = pd.DataFrame, i = 0):
    if parsed:
        return func(json.load(open("parsed" +   table + '.JSON')))
    else:
        if not i:
            return func(json.load(open(table + '.JSON')))
        else:
            return func(json.load(open(table + '_number_' + str(i) + '.JSON')))

def getAllUA(alpha_F = 0, beta_F = 0, alpha_kiro = 1, beta_kiro = 1):
    check = lambda x: 0 if (isnan(x) or x == None) else x
    return float(f'{(check(alpha_F) / check(alpha_kiro) + check(beta_F) / check(beta_kiro)):.2f}')

def defineRaoType(UA, rao, metal):
    rao = rao.set_index(['material'])
    if metal:
        for i in rao:
            if UA <= rao.at["Metal",i]:
                return i
    else:
        for i in rao:
            if UA <= rao.at["Not Metal",i]:
                return i

def createTable(table, tablename = "table", xlsx = False, keepJSON = False):
    with open(tablename +".JSON","w") as f:
        f.write(json.dumps(table))
    if xlsx:
        table = pd.read_json(tablename+".JSON")
        table.to_excel(tablename+".xlsx", index = False)
    else:
        keepJSON = True
    if not keepJSON:
        remove(tablename+".JSON")


def main(number = 0):
    rao = jsonRead("RaoBorders", parsed = False)
    cwd = getcwd()
    chdir(cwd + "/test")
    floor = jsonRead("PointsFloor", parsed = False, i = number)
    square = jsonRead("SquaresFloor", parsed = False, i = number)
    volume = floor[floor["room_name"].isin(square["room_name"].unique())]
    volume = volume.reset_index()
    volume = volume.drop(columns = ["index"])
    print("Correctness of Volume dataframe creation:", square["room_name"].unique().sort() == volume["room_name"].unique().sort())
    

    mat = jsonRead("Materials", parsed = False, i = number)
    matc = jsonRead("MaterialsCoef", parsed = False, i = number)
    
    all_UA = []
    for i in range(min(len(volume['alpha_F']), len(volume['beta_F']))):
        all_UA.append(getAllUA(volume.at[i, 'alpha_F'], volume.at[i, 'beta_F'], mat.at[i, 'alpha_kiro'], mat.at[i, 'beta_kiro']))
    volume = volume.assign(all_UA = pd.Series(all_UA))
    
    print("Input value of variable `after`: ", end = '')
    after = int(input())
    if after:
        volume['all_UA'] = (volume['all_UA'] / 2).round(2) #placeholder
    
    rao_UA = []
    for i in range(len(volume['all_UA'])):
        rao_UA.append(defineRaoType(volume.loc[i,'all_UA'], rao, mat.loc[i,'metal']))
    volume = volume.assign(RAO = pd.Series(rao_UA))
    volume_aggmat = volume.groupby(by = ['room_name', 'material']).sum()['quantity'] 
    volume_aggrao = volume.groupby(by = ['room_name', 'material', 'RAO']).sum()['quantity']
    volume_aggrao_concat = pd.pivot_table(pd.DataFrame(volume_aggrao), index=['room_name', 'material'], columns = ['RAO'], values = ['quantity'])
    volume_aggmat_concat = pd.pivot_table(pd.DataFrame(volume_aggmat), index=['room_name', 'material'], values = ['quantity'])
    volume = volume.merge(volume_aggrao_concat, how = 'left', on = ['room_name', 'material'])
   # volume.columns = ["id", "room_name", "material", "alpha_UA", "beta_UA", "alpha_F", "beta_F", "gamma_EP", "quantity", "files_id", "all_UA", "RAO", "moi", "nao", "onrao", "prom", "sao"]
    names = []
    for name in volume.columns:
        print(name)
        if name not in ["id", "room_name", "material", "alpha_UA", "beta_UA", "alpha_F", "beta_F", "gamma_EP", "quantity", "files_id", "all_UA", "RAO"]:
            names.append(str(name).lstrip("(\'quantity\',").strip("\'() \'"))
        else:
            names.append(name)
    volume.columns = names
    print(volume.columns)
    volume = volume.merge(volume_aggmat_concat, how = 'left', on = ['room_name', 'material'])
    print(volume)
    for col in volume["RAO"].unique():
        volume[col+"_part"] = volume[col] / volume['quantity_y']
    volume = volume.merge(pd.DataFrame({"id": mat.loc[mat["id"].isin(volume["id"])]["id"], "coefLoosening": 1/mat.loc[mat["id"].isin(volume["id"])]['coef_density_change']}), how = "left", on = ["id"])
    square['square*width'] = square['square'] * matc['width']
    volume = volume.merge(square[['id', 'square*width']], on='id', how='left')
    volume['tempCoef'] = volume['coefLoosening'] * volume['square*width']
    chdir(cwd)
    for col in volume["RAO"].unique():
        volume[col+"_part*tempCoef"] = volume[col+"_part"] * volume['tempCoef']
    createTable(volume.to_dict('records'), "volume_" + str(number), xlsx = True)
    return 0
    
def tester():
    print("Amount of unique versions of tables created:", end = '')
    num = int(input())
    for i in range(1, num+1):
        main(i)
tester()
