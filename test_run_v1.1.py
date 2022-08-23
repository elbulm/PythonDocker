import pandas as pd
import json
from math import isnan
from os import remove
from os import mkdir
from os import chdir
from os import getcwd




def jsonRead(table, parsed = True, func = pd.DataFrame, i = 0):
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
        return func(json.load(open("parsed" +   table + '.JSON')))
    else:
        if not i:
            return func(json.load(open(table + '.JSON')))
        else:
            return func(json.load(open(table + '_number_' + str(i) + '.JSON')))

def getAllUA(alpha_F = 0, beta_F = 0, alpha_kiro = 1, beta_kiro = 1):
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
    
    """
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
    """
    Creates files for tables, either xlsx, JSON or both.
    
    P.S. It creates both files and rewrites a JSON anyway, due to
    default json.dumps method being unable to read nan as np.nan,
    instead reading it as string 'nan'. This was way too problematic and
    there was no built-in solution, so I decided to leave it as is — now it
    works slightly slower, but it works.
    """
    with open(tablename +".JSON","w") as f:
        f.write(json.dumps(table, allow_nan = True))
    table = pd.read_json(tablename+".JSON")
    table.to_excel(tablename+".xlsx", index = False)
    with open(tablename + ".JSON","w") as f:
        f.write(json.dumps(pd.read_excel(tablename + '.xlsx').to_dict('records'))) #otherwise nans will be read as strings for some reason and everything breaks
    if not xlsx:
        keepJSON = True
        remove(tablename +".xlsx")
    if not keepJSON:
        remove(tablename +".JSON")


def main(number = 0):
    #   there tables are read and volume dataframe is created
    rao = jsonRead("RaoBorders", parsed = False)
    cwd = getcwd()
    chdir(cwd + "/test")
    floor = jsonRead("PointsFloor", parsed = False, i = number)
    square = jsonRead("SquaresFloor", parsed = False, i = number)
    mat = jsonRead("Materials", parsed = False, i = number)
    matc = jsonRead("MaterialsCoef", parsed = False, i = number)
    volume = floor[floor["room_name"].isin(square["room_name"].unique())]
    volume = volume.reset_index()
    volume = volume.drop(columns = ["index"])
    print("Correctness of Volume dataframe creation:", square["room_name"].unique().sort() == volume["room_name"].unique().sort())
   
    #   all_UA variable is added to volume dataframe here
    all_UA = []
    for i in range(min(len(volume['alpha_F']), len(volume['beta_F']))):
        all_UA.append(getAllUA(volume.at[i, 'alpha_F'], volume.at[i, 'beta_F'], mat.at[i, 'alpha_kiro'], mat.at[i, 'beta_kiro']))
    volume = volume.assign(all_UA = pd.Series(all_UA))
    
    #   further calculatuons are made according to 'after' variable value
    print("Input value of variable `after`: ", end = '')
    after = int(input())
    if after:
        placeholder = 2 #because needed coefficient was not provided
        volume['all_UA'] = (volume['all_UA'] / placeholder).round(2)
    
    #   adds a column to volume that determines which rao type the observation belongs to
    rao_UA = []
    for i in range(len(volume['all_UA'])):
        rao_UA.append(defineRaoType(volume.loc[i,'all_UA'], rao, mat.loc[i,'metal']))
    volume = volume.assign(RAO = pd.Series(rao_UA))
    
    #   counts quantity by room and material type and converts it to new tables that appends
    volume_aggmat = volume.groupby(by = ['room_name', 'material']).sum()['quantity'] 
    volume_aggrao = volume.groupby(by = ['room_name', 'material', 'RAO']).sum()['quantity']
    volume_aggrao_concat = pd.pivot_table(pd.DataFrame(volume_aggrao), index=['room_name', 'material'], columns = ['RAO'], values = ['quantity'])
    volume_aggmat_concat = pd.pivot_table(pd.DataFrame(volume_aggmat), index=['room_name', 'material'], values = ['quantity'])
    volume = volume.merge(volume_aggrao_concat, how = 'left', on = ['room_name', 'material'])
    
    #   this part fixes broken naming that was automatically done by
    #   combination of group_by and pivot_table.
    names = []
    for name in volume.columns:
        if name not in ["id", "room_name", "material", "alpha_UA", "beta_UA", "alpha_F", "beta_F", "gamma_EP", "quantity", "files_id", "all_UA", "RAO"]:
            names.append(str(name).lstrip("(\'quantity\',").strip("\'() \'"))
        else:
            names.append(name)
    volume.columns = names
    
    #   finds proportion of rao type in the room to all rao in same room
    volume = volume.merge(volume_aggmat_concat, how = 'left', on = ['room_name', 'material'])
    for col in volume["RAO"].unique():
        volume[col+"_part"] = volume[col] / volume['quantity_y']
    
    #   does other interim calculations that result in tempCoef column
    volume = volume.merge(pd.DataFrame({"id": mat.loc[mat["id"].isin(volume["id"])]["id"], "coefLoosening": 1/mat.loc[mat["id"].isin(volume["id"])]['coef_density_change']}), how = "left", on = ["id"])
    square['square*width'] = square['square'] * matc['width']
    volume = volume.merge(square[['id', 'square*width']], on='id', how='left')
    volume['tempCoef'] = volume['coefLoosening'] * volume['square*width']
    
    #   final calculations for each rao type
    for col in volume["RAO"].unique():
        volume[col+"_part*tempCoef"] = volume[col+"_part"] * volume['tempCoef']
    
    #   creates final volume table
    chdir(cwd)
    createTable(volume.to_dict('records'), "volume_" + str(number), xlsx = True)
    return 0
    
def tester():
    """
    just a superstructure of main function to repeat it several times
    """
    print("Amount of unique versions of tables created:", end = '')
    num = int(input())
    for i in range(1, num+1):
        main(i)
tester()
