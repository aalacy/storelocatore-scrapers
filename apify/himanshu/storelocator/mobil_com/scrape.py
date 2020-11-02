import csv
import re
from sgrequests import SgRequests
from geo_grid import *
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mobil_com')




session = SgRequests()

def mk_csv_writer(output_file):
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    # Header
    writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                     "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                     "page_url"])
    return writer

def fetch_data(box: Rect) -> list:

    params = {
        "Latitude1": str(box.south_west.lat),
        "Longitude1": str(box.south_west.lng),
        "Latitude2": str(box.north_east.lat),
        "Longitude2": str(box.north_east.lng),
        "DataSource": "RetailGasStations",
        "Country": "US",
        "Customsort": "False"
    }

    base_url = "https://www.exxon.com/en/api/locator/Locations"

    r = session.get(base_url, params = params).json()

    for exxon in r:
        store = []
        store.append("https://www.mobil.com")
        store.append(exxon['DisplayName'])
        if "AddressLine2" not in exxon:
            store.append(exxon['AddressLine1'])
        else:
            store.append(exxon['AddressLine1'] + " "+exxon['AddressLine2'])
        try:
            store.append(exxon['City'])
        except:
            store.append("MISSING")
        try:
            store.append(exxon['StateProvince'])
        except:
            store.append("<MISSING>")
        try:
            store.append(exxon['PostalCode'])
        except:
            store.append("<MISSING>")
        if exxon['Country']=="Canada":
            store.append("CA")
        else:
            store.append(exxon['Country'])

        store.append(exxon["LocationID"])

        if exxon['Telephone']:
            phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(exxon['Telephone']))
            if phone_list:
                store.append(phone_list[0])
            else:
                store.append("<MISSING>")

        else:
            store.append("<MISSING>")

        loc_slug = " ".join(re.findall(r"[a-zA-Z0-9]+", exxon["DisplayName"])).lower().replace(" ","-").strip()
        page_url = "https://www.exxon.com/en/find-station/"+exxon['City'].replace(" ","-").lower().strip()+"-"+exxon['StateProvince'].lower().strip()+"-"+str(loc_slug)+"-"+exxon["LocationID"]
        if "exxon" in exxon['BrandingImage']:
            location_type = "exxon"
            store.append(location_type)
        elif "mobil" in exxon['BrandingImage']:
            location_type="mobil"
            store.append(location_type)
        else:
            logger.info("!Unknown location type, skipping! Branding img:" + exxon['BrandingImage'])
            yield []
            continue

        store.append(exxon['Latitude'])
        store.append(exxon['Longitude'])
        try:
            store.append(exxon['WeeklyOperatingHours'].replace('<br/>',','))
        except:
            store.append("<MISSING>")
        store.append(page_url)

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store

def record_id(rec) -> str:
    # using lat,long for id, since store number fails a few times, resulting in duplicate rows.
    return f"{str(rec[10])},{str(rec[11])}"

def scrape():
    # no results for alaska & hawaii
    continental_us = Rect.ne_sw(north_east=Coord.safely_create(53, -54), south_west=Coord.safely_create(19, -136))

    max_results = 250 # know based on manual testing.

    with open('data.csv', mode='w',newline="") as output_file:
        writer = mk_csv_writer(output_file)

        for store in GeoGrid.divide_and_conquer(box=continental_us,
                                                search_in_rect_fn=fetch_data,
                                                identity_fn=record_id,
                                                max_results_per_search=max_results):
            if store:
                writer.writerow(store)

scrape()