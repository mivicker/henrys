import pandas as pd
import os

def create_route_list(working_path, date, time, route_name, route_df):
    route_df = route_df.copy()
    route_df['Box'] = (route_df["Box Type"]
                    + " " + route_df["Box Menu"]
                    + " " + route_df["Box Size"])
    route_df = route_df.drop(['Route #', 'Geocoded Address', 'Delivery Size',
       'Delivery ID', 'Box Menu', 'Box Size', 'Box Type',
       'Call Status', 'CustomerServiceAssignment', 'DairyFree',
       'Delivery Date', 'Delivery Status', 'DeliveryDay',
       'DeliveryNumber', 'DeliveryTime', 'DeliveryZone',
       'First Name', 'HealthPlan', 'PeanutFree', 'Primary Language', 'State',], axis = 1)

    route_df = route_df[['Stop #', 'Address', 'City', 'ZIP', 'Box', 
        'Delivery Notes', 'MainContact', 'Member ID', 'Phone', 'TextOptIn']]
    route_df.index = route_df['Stop #']
    route_df = route_df.drop('Stop #', axis = 1)

    date_path = date.strftime("%m-%d-%Y")

    output_path = os.path.join(
        working_path,
        date_path,
        time,
        f'{route_name}List{time}.csv'
    )

    route_df.to_csv(output_path)

def create_van_manifest(working_path, date, time, route_name, route_df):
    matrix_path = os.path.join(working_path, 'templates', 'manifestmatrix.csv')

    df = pd.read_csv(matrix_path)
    df['Name'] = df['Item Code'] + ' - ' + df['Description']
    df.index = df['Name']

    distill_a = route_df[['Stop #', 'Member ID','Box Type', 'Box Menu', 'Box Size']]
    distill_b = distill_a[['Stop #', 'Member ID']].copy()
    distill_b['Box'] = distill_a['Box Type'] + ' ' + distill_a['Box Menu'] + ' ' + distill_a['Box Size']

    out = distill_b.join(df.T, on='Box')

    date_path = date.strftime("%m-%d-%Y")

    output_path = os.path.join(
        working_path,
        date_path,
        time,
        f'{route_name}Manifest{time}.csv'
        )

    out.to_csv(output_path)