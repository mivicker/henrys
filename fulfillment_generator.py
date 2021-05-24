import os
import string
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import config

path = os.path.join(config.base_dir, '05-24-2021', 'PM', 'RoutesPM.csv')

test_delivs = pd.read_csv(path)

test_delivs['Box'] = test_delivs[['Box Menu', 'Box Size', 'Box Type']].apply(
    (lambda x: " ".join([x[2], x[0], x[1]])), axis=1)

def exchange_product(
    row, condition, product_to_remove, product_to_add, ratio):
    if row[condition] == "Yes":
        quantity = row[product_to_remove]
        row[product_to_remove] = row[product_to_remove] - quantity
        row[product_to_add] = row[product_to_add] + quantity * ratio
        return row
    return row

def route_num_to_letter(name):
    _, num = name.split()
    index = int(num) - 1
    return string.ascii_uppercase[index]

test_delivs["Route #"] = test_delivs["Route #"].apply(route_num_to_letter)

matrix_path = os.path.join(config.base_dir, 'menumatrix.csv')
df = pd.read_csv(matrix_path)

df.index = df["Item Code"]

items_table = df[["Item Code", "Description", "Storage"]]
menus_table = df[df.columns[3:]]

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('templates/fulfillmentsheet.html')

def create_order_dictionary(date, time, routes_df, menu_df, product_df):
    return {
        'date': date,
        'time': time,
        'routes': create_routes_list(routes_df, menu_df, product_df)
           }

def create_routes_list(routes_df, menu_df, product_df):
    routes = routes_df.groupby('Route #')
    return [create_route_dictionary(
        route_name, routes.get_group(route_name), menu_df, product_df) 
           for route_name in routes.groups]

def create_route_dictionary(route_name, route_df, menu_df, product_df):
    return {
        'name': route_name,
        'stops': create_stops_list(route_df, menu_df, product_df)
    }

def create_stops_list(route_df, menu_df, product_df):
    return [create_stop_dictionary(stop_row[1], menu_df, product_df) 
            for stop_row in route_df.iterrows()]

def create_stop_dictionary(stop_data, menu_df, product_df):
    racks = get_racks(stop_data['Box'], menu_df, product_df)
    stop_data["Racks"] = racks
    return stop_data

def build_exchange_func(product_to_remove, product_to_add, ratio):
    def exchange(row):
        original_quantity = row[product_to_remove]
        row[product_to_remove] = 0
        row[product_to_add] = (row[product_to_add] 
                             + original_quantity * ratio)
        return row
    return exchange

def make_exchanges()
    pass

def get_menu_list(box, menu_df, product_df, exchanges):
    menu_col = menu_df[box]
    filt = menu_col.astype(bool)
    item_list = menu_col[filt]
    item_df = product_df.join(item_list, how='right')
    item_df.rename(columns={box:"Quantity"}, inplace=True)
    return item_df

def get_racks(box, menu_df, product_df):
    menu_items = get_menu_list(box, menu_df, product_df)
    racks = menu_items.groupby('Storage')
    ordered_racks = sort_racks(racks.groups)
    return [create_rack_dictionary(group, racks.get_group(group)) 
            for group in ordered_racks]

def create_rack_dictionary(name, rack_df):
    return {
        'name': name,
        'items': create_items_list(rack_df)
    }

def sort_racks(rack_groups):
    rack_order = ['Dry Rack 1',
             'Dry Rack 2',
             'Cooler Rack',
             'Produce Rack',
             'Bakery Trays',
             'Dock']
    active_racks = [group for group in rack_groups]
    return [rack for rack in rack_order if rack in active_racks]
    
def create_items_list(rack_df):
    return rack_df.to_dict(orient='records')

order = create_order_dictionary('05-24-2021', 'PM', test_delivs, menus_table, items_table)

rendered = template.render(order=order)
with open('templates\\test.html', 'w') as f:
    f.write(rendered)