import os
import pandas as pd

def condition_columns(df):
    return df[['Delivery ID', 'Address', 'City', 'State', 'ZIP', 'Box Menu', 'Box Size', 'Box Type',
       'Call Status', 'CustomerServiceAssignment', 'DairyFree',
       'Delivery Date', 'Delivery Notes', 'Delivery Status', 'DeliveryDay',
       'DeliveryNumber', 'DeliveryTime', 'DeliveryZone',
       'First Name', 'HealthPlan', 'MainContact', 'Member ID', 'PeanutFree',
       'Phone', 'Primary Language',  'TextOptIn',]]

def check_box_types(df):
    return df["Box Type"].isnull().any()

def filt_for_day(df, day):
    df["Delivery Date"] = df["Delivery Date"].apply(lambda x: x.date())
    filt = df["Delivery Date"] == day
    return df[filt]

def filt_for_future(df):
    future_filt = df["Delivery Status"] == 'Future'
    pick_up_filt = df["Delivery Status"] == "Future - Pick up"
    remaining_filt = ~(future_filt | pick_up_filt)
    if not df[remaining_filt].empty:
        print("The following entries were filtered out.")
        print(df[remaining_filt][["MainContact", "Member ID", "Delivery Status"]])
    return df[future_filt], df[pick_up_filt]

def split_covenant(df):
    covenant_filt = df['HealthPlan'] == 'Covenant'
    return df[covenant_filt], df[~covenant_filt]

def split_am_pm(df):
    #Split the days deliveries into morning and afternoon.
    am_filt = df["DeliveryTime"].str.upper() == "AM"
    pm_filt = df["DeliveryTime"].str.upper() == "PM"

    left_overs = df[~am_filt & ~pm_filt] 
    if not left_overs.empty:
        print("The following entries have no delivery time:")
        print(left_overs[["MainContact", "Member ID", "Delivery Status"]])

    am_df = df[am_filt]
    pm_df = df[pm_filt]

    return am_df, pm_df

def make_date_directory(day, time, location):
    date_string = str(day.strftime("%m-%d-%Y"))
    if time:
        dir_name = os.path.join(location, date_string, time)
    else:
        dir_name = os.path.join(location, date_string)

    os.mkdir(dir_name)
    print(f"created directory for {date_string}, {time}")

    return dir_name

def fill_empty_box_type(df, constituents_df):
    merged_df = df.merge(
        constituents_df[["Member ID", "BoxType"]], 
        how="left", on ="Member ID")
    
    if len(merged_df) != len(df):
        raise ValueError(
            'The merged df doesn\'t have the same length as input')

    merged_df["Box Type"].fillna(
        merged_df["BoxType"], inplace=True)
    merged_df.drop("BoxType", axis=1, inplace=True)
    return merged_df

def select_date_range(df, starting, ending):
    low_bound = pd.Timestamp(starting)
    upper_bound = pd.Timestamp(ending)
    date_filt = (df["Delivery Date"] >= low_bound) & (df["Delivery Date"] <= upper_bound)
    return df[date_filt]

def lister(counts, values):
    """
    Create a list with each element from values repeated
    the corresponding number in counts. 
    """
    if len(counts) != len(values):
        raise Exception("Length of counts must equal length of values.")
    if not counts or not values:
        return []
    
    work = [values.pop()] * counts.pop()
    return lister(counts, values) + work

def fill_covenant_row(box, date):
    row = {
        'Member ID': '00000000', 
        'MainContact': 'Centering Pregnancy', 
        'HealthPlan': 'Covenant', 
        'Box': box, 
        'PeanutFree': 'No', 
        'DairyFree': 'No',
        'Delivery Date': date,
        'DeliveryTime': 'AM'
    }
    return row

def add_covenant_rows(df, counts, boxes, dates):
    """
    Input: a Dataframe, a list of counts, a list of boxes.
    Output: Dataframe with proper counts of rows added 
    """
    row_templates = [fill_covenant_row(box, date) for box, date in zip(boxes, dates)]
    rows = lister(counts, row_templates)
    
    return df.append(rows)

def exchange_product(
    row, condition, product_to_remove, product_to_add, ratio):
    if row[condition] == "Yes":
        quantity = row[product_to_remove]
        row[product_to_remove] = row[product_to_remove] - quantity
        row[product_to_add] = row[product_to_add] + quantity * ratio
        return row
    return row

def start_date_filt(on_date, time):
    if time == "AM":
        return on_date
    filt = on_date["DeliveryTime"] == "PM"
    return on_date[filt]
    
    #grab the deliveries on the end date, only AM if AM or AM and PM if PM

def end_date_filt(on_date, time):
    if time == "PM":
        return on_date
    filt = on_date["DeliveryTime"] == "AM"
    return on_date[filt]

def calc_replacement(filtered_df, row):
    orig_product = row["Original ID"]  + " -> " + row["Original"]
    quantity = filtered_df[orig_product].sum()
    if not row["Replacement ID"]:
        return orig_product, quantity * -1
    
    replacement_product = str(row["Replacement ID"])  + " -> " + str(row["Replacement"])
    replacement_ratio = row["Replacement per Original Unit"]
    
    return [orig_product, replacement_product], [quantity * -1, quantity * replacement_ratio]

def count_substitutions(subs_df, sum_df, menu_df):
    adjustment_series = pd.Series(index=menu_df.index, data=0)

    for _, row in subs_df.iterrows():
        #grab the deliveries between the two dates
        date_filt = ((sum_df["Delivery Date"].dt.date > row["Date Start"]) 
                   & (sum_df["Delivery Date"].dt.date < row["Date End"]))
        adjustment_df = sum_df[date_filt]

        #grab the deliveries on the start date, only AM or PM if am, or just PM if PM
        date_filt = sum_df["Delivery Date"] == row["Date Start"]
        on_date = sum_df[date_filt]
        on_date = start_date_filt(on_date, row["Time Start"])

        adjustment_df.append(on_date)

        date_filt = sum_df["Delivery Date"] == row["Date End"]
        on_date = sum_df[date_filt]
        on_date = end_date_filt(on_date, row["Time End"])

        adjustment_df.append(on_date)

        replacements, quantities = calc_replacement(adjustment_df, row)

        adjustment_series.loc[replacements] += quantities
        
    return adjustment_series

def check_overlap(new_start, new_end, existing_start, existing_end):
    return new_start <= existing_end and existing_start <= new_end

def check_invoice_overlap(prev_invoices, starting, ending):
    return any(prev_invoices.apply(
        lambda x: check_overlap(
            starting, ending, x['Period Start'], x['Period End']), axis=1))