import os
import sys
import string
import pandas as pd
from openpyxl import Workbook, load_workbook
import config
from utils.command_utils import validate_arguments
from utils.van_manifest import create_route_list, create_van_manifest
from utils.pick_utils import make_pick_list

def route_num_to_letter(name):
    route, num = name.split()
    index = int(num) - 1
    return route + " " + string.ascii_uppercase[index]

def make_selector(box_type, box_menu):
    box_type = translate_box_type(box_type)
    return box_type + ' ' + box_menu

def make_sheet_name(stop_num, menu_selector):
    return  f"{stop_num} - {menu_selector}"

def translate_box_type(_type):
    translations = {
        "Standard":"Std", 
        "Vegetarian":"Veg", 
        "Halal":"Halal", 
        "Kidney Friendly":"Kidney"
    }
    try:
        return translations[_type]
    except KeyError:
        print('ERROR: An important field is missing. Often one of the entries is missing its box type.')
        sys.exit(1)

def fill_sheet(template, data):
    menu_range = range(14,45)
    size_to_columns = {
        'Small': 'C',
        'Family': 'D',
        'Large Family': 'E'
    }
    sizes = list(size_to_columns.keys())

    template_fields = {
    "Delivery Date" : "B3",
    "Stop #" : "B4",
    "Member ID" : "B5",
    "MainContact" : "B6",
    "Box Size" : "B7",
    "first_delivery" : "F4",
    "PeanutFree" : "B10",
    "DairyFree" : "F10",
    "HealthPlan" : "E5",
    "delivery_notes" : "A9",
    "DeliveryTime": "D3",
    "Route #": "F3"
    }
    
    #There must be some more idomatic way of doing this.
    fillable_fields = list(template_fields.keys())
    fillable_fields.remove('first_delivery')
    fillable_fields.remove('delivery_notes')

    #Delete all the numbers on the template not corresponding to the current menu.
    data['Route #'] = route_num_to_letter(data['Route #'])

    sizes_ins = sizes
    sizes_ins.remove(data["Box Size"])
    for size in sizes_ins:
        for row in menu_range:
            col = size_to_columns[size]
            template[f'{col}{row}'] = ''


    for field in fillable_fields:
        cell = template_fields[field]
        template[cell] = str(data[field]).upper()

    first_cell = template_fields["first_delivery"]
    if data["DeliveryNumber"] == 1:
        template[first_cell] = "YES"
        
    else:
        template[first_cell] = "NO"

    notes_cell = template_fields['delivery_notes']
    if str(data['Delivery Notes']) != 'nan':
        template[notes_cell] = f"NOTES: {data['Delivery Notes']}"

def create_fulfillment_books(df, date, time, working_path, wb_path):
    routes = set(df["Route #"])

    for route in routes:
        filt = df["Route #"] == route
        route_df = df[filt]

        if route == "DISMISSED REQUEST":
            dismissed = len(route_df)
            continue

        route_name = route_num_to_letter(route)
        #Read a fresh template workbook every route
        template_wb = load_workbook(wb_path)

        date_path = date.strftime("%m-%d-%Y")

        filename = os.path.join(working_path, date_path, time, f"{date}--{time}-{route_name}.xlsx")

        #working_path, date, time, route_name, route_df
        #create_van_manifest(working_path, date, time, route, route_df)
        create_route_list(working_path, date, time, route_name, route_df)

        live_sheets = []

        for stop in route_df.iterrows():
            data = stop[1]
            stop_num = data["Stop #"]
            menu_selector = make_selector(data["Box Type"], data["Box Menu"])

            #select correct worksheet and copy
            template = template_wb[menu_selector]
            template = template_wb.copy_worksheet(template)

            #properly rename the sheet
            template.title = make_sheet_name(stop_num, menu_selector)
            live_sheets.append(template.title)

            fill_sheet(template, data)

        #clean up the empty templates
        for sheet in template_wb.worksheets:
            if sheet.title not in live_sheets:
                template_wb.remove(sheet)

        #save the workbook - this should have a naming convention based on the route and date.
        template_wb.save(filename)

    print(f"Warning: {dismissed} item(s) not included, check all deliveries spreadsheet.")

if __name__ == "__main__":
    working_path = config.base_dir
    date = validate_arguments(sys.argv)
    wb_path = os.path.join(working_path, "templates", "Fulfillment Tickets.xlsx")
    date_path = date.strftime("%m-%d-%Y")

    for time in [
        "AM", 
        "PM",
        "Covenant"]:
            filename = f"Routes{time}.csv"

            route_path = os.path.join(working_path, date_path, time, filename)
            try:
                df = pd.read_csv(route_path)
            except:
                print(f"ERROR: Failed to find Routes{time}.csv. Perhaps it is not named correctly.")
                sys.exit(1)

            df["Member ID"] = df["Member ID"].astype(int, copy=True, errors='ignore')
        
            create_fulfillment_books(df, date, time, working_path, wb_path)
            make_pick_list(time, date_path)            
            print(f"Created route documents for {date_path} {time}")
