import sys
import os
import config
from utils.command_utils import validate_arguments
from henrys_helpers import (fill_empty_box_type, condition_columns,
    check_box_types, filt_for_day, filt_for_future, split_am_pm, 
    make_date_directory, split_covenant)
from sharepointless import load_df_from_sharepoint, get_app_password

#Input: (optional custom date), also reads the table in the DownloadViewData file
#Output: am and pm csvs of all the deliveries that are on for the next day (monday in the case if friday)
#this needs to be placed in new directory with the next day's date and the csv should be named AllDeliveries

if __name__ == "__main__":
    #The path to the healthcare working directory.
    working_path = config.base_dir
    
    #check if the user input a particular date, otherwise return next biz day's results
    day = validate_arguments(sys.argv)
    
    #ask the user for their sharepoint credentials
    username, password = get_app_password()

    base_url = config.base_url
    dms_url = config.dms_url

    list_name = "Deliveries"
    view_name = "Windowed Delivery View"

    df = load_df_from_sharepoint(
        base_url, dms_url, list_name, view_name, username, password)

    #Filters for the chosen day
    target_df = filt_for_day(df, day)
    target_df, pick_ups = filt_for_future(target_df.copy())
    target_df = condition_columns(target_df)

    #fills in missing box types
    list_name = "Constituents"
    view_name = "All Items"

    constituents_df = load_df_from_sharepoint(
        base_url, dms_url, list_name, view_name, username, password)
    
    target_df = fill_empty_box_type(target_df, constituents_df)

    covenant_df, target_df = split_covenant(target_df)

    #Splits df into morning and afternoon
    am, pm = split_am_pm(target_df)

    #make date directory
    make_date_directory(day, '', working_path)

    #checks if timeslots have stops and saves csv if so.
    if not am.empty:
        #Create a new dir that will hold all information for the time
        folder = make_date_directory(day, 'AM', working_path)
        am_path = os.path.join(folder, 'AllDeliveriesAM.csv')
        #save the csv
        if check_box_types(am):
            print("AM is missing box types. Fix this before going forward.")
        am.to_csv(am_path)
    if not pm.empty:
        folder = make_date_directory(day, 'PM', working_path)
        pm_path = os.path.join(folder, 'AllDeliveriesPM.csv')
        if check_box_types(pm):
            print("PM is missing box types. Fix this before moving forward.")
        pm.to_csv(pm_path)

    if not pick_ups.empty:
        folder = make_date_directory(day, 'PickUps', working_path)
        pick_ups.to_csv(f'{folder}\\AllPickups.csv')

    if not covenant_df.empty:
        folder = make_date_directory(day, 'Covenant', working_path)
        covenant_df.to_csv(f'{folder}\\Covenant.csv')