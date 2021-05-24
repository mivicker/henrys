import os
import unittest
import pandas as pd

import config
from henrys_helpers import (split_am_pm, condition_columns, 
    filt_for_day, filt_for_future, split_covenant, fill_empty_box_type)
from sharepointless import load_df_from_sharepoint, get_app_password

class TestOne(unittest.TestCase):
    def setUp(self) -> None:
        def get_test_path(time):
            return os.path.join('fixtures', time, f'AllDeliveries{time}.csv')
        self.test_am_df = pd.read_csv(get_test_path('AM'))
        self.test_pm_df = pd.read_csv(get_test_path('PM'))
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_split_am_pm(self):
        data = {'DeliveryTime': ['AM', 'AM', 'AM', 'PM', 'PM'],
                'Name': ['Susu','Susu','Susu','Harvey','Harvey',]}
        df = pd.DataFrame.from_dict(data)

        am, pm = split_am_pm(df)

        self.assertTrue(all(am['Name'] == 'Susu'))
        self.assertTrue(all(pm['Name'] == 'Harvey'))

    def test_get_sharepoint_list(self):
        username, password = get_app_password()
        base_url = config.base_url
        dms_url = config.dms_url

        day = '2021-05-11'

        list_name = "Deliveries"
        view_name = "Windowed Delivery View"

        df = load_df_from_sharepoint(
            base_url, dms_url, list_name, view_name, username, password)

        target_df = filt_for_day(df, day)
        target_df, pick_ups = filt_for_future(target_df.copy())
        target_df = condition_columns(target_df)

        list_name = "Constituents"
        view_name = "All Items"

        constituents_df = load_df_from_sharepoint(
            base_url, dms_url, list_name, view_name, username, password)

        target_df = fill_empty_box_type(target_df, constituents_df)

        _, target_df = split_covenant(target_df)

        am, pm = split_am_pm(target_df)

        self.assertTrue(am.equals(self.test_am_df))
        self.assertTrue(pm.equals(self.test_pm_df))

if __name__ == "__main__":
    unittest.main()