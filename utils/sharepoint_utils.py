from shareplum import Site
from shareplum import Office365
import json
import pandas as pd

def get_list_from_sharepoint(list_name, view_name='All Items'):
    with open('secret.json') as f:
        secret = json.load(f)

    authcookie = Office365(
        'https://gcfbsm.sharepoint.com', 
        username='mvickers@gcfb.org', 
        password=secret["PASSWORD"]
        ).GetCookies()

    site = Site('https://gcfbsm.sharepoint.com/sites/DMS', authcookie=authcookie)
    sp_list = site.List(list_name)

    entries = sp_list.get_list_items(view_name=view_name)

    df = pd.DataFrame(entries)

    return df