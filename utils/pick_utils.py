import os
import pandas as pd

def make_pick_list(time, date):

    base_dir = 'C:\\Users\\mvickers\\Gleaners Community Food Bank\\Healthcare Programs - Healthcare Working Directory'
    filename = f"Routes{time}.csv"
    path = os.path.join(base_dir, date, time, filename)
    delivs_df = pd.read_csv(path)

    delivs_df["Box"] = delivs_df["Box Type"] + " " + delivs_df["Box Menu"] + " " + delivs_df["Box Size"]

    delivs_df["Box"] = delivs_df["Box"].str.replace("Large Family","Large")
    delivs_df["Box"] = delivs_df["Box"].str.replace("Kidney Friendly","Healthy Kidney")

    delivs_df = delivs_df[["Member ID", "MainContact", "Box"]]

    filename = "menumatrix.csv"
    path = os.path.join(base_dir, filename)
    menu_df = pd.read_csv(path)

    pick_prods = [
        'MG1186',
        'MG1063',
        'MG1024',
        'MG1380',
        'MG1048',
        'MG1241',
        'MG1385P',
        'MG1286',
        'MG1181',
        'MG1178',
        'MG1214',
        'MG1384P'
    ]

    filt = menu_df["Item Code"].isin(pick_prods)

    menu_df = menu_df[filt]

    menu_df.index = menu_df["Item Code"] + " - " + menu_df["Description"]

    menu_df = menu_df.drop(["Item Code", "Description"], axis = 1)

    all_prods = delivs_df.join(menu_df.T, on = "Box")

    filename = "PickList.csv"

    output_path = os.path.join(base_dir, date, time, filename)

    all_prods = all_prods.drop(['Member ID', 'MainContact', 'Box'], axis = 1)
    summary = all_prods.sum()
    filt = summary != 0
    summary = summary[filt]
    summary.to_csv(output_path)