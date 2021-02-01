from sgrequests import SgRequests
import pandas as pd

session = SgRequests()

canada_state_codes = [
    "NL",
    "PE",
    "NS",
    "NB",
    "QC",
    "ON",
    "MB",
    "SK",
    "AB",
    "BC",
    "YT",
    "NT",
    "NU",
]
# Declare needed lists
locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

# Get all services
serve_url = "https://webapp3.sallynet.org/api.locator/api/Services"
services_resp = session.get(serve_url).json()
services_resp.pop(0)

serve_dict = {}
for serve in services_resp:
    serve_dict[serve["Name"]] = serve["Id"]

# Loop through services offerred to create lists of all location types
for key in serve_dict:

    serve_url = (
        "https://webapp3.sallynet.org/api.locator/api/Locations/search/?countToReturn=999&serviceId="
        + str(serve_dict[key])
    )
    serve_resp = session.get(serve_url).json()

    for location in serve_resp:
        state = location["ProvinceCode"]

        locator_domains.append("https://salvationarmy.ca/")
        page_urls.append("https://salvationarmy.ca/locator")
        location_names.append(location["Name"])
        street_addresses.append(location["Street"])
        citys.append(location["City"])
        states.append(location["ProvinceCode"])
        zips.append(location["Postal"])
        store_numbers.append(location["Id"])
        phones.append(location["Phone"])
        latitudes.append(str(location["Latitude"]))
        longitudes.append(str(location["Longitude"]))
        hours_of_operations.append("<MISSING>")

        if state in canada_state_codes:
            country_codes.append("CA")
        else:
            country_codes.append("<MISSING>")
        location_types.append(key)

location_types_df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

# 81 locations have no declared location type, gather all here to then fit those 81 in
all_url = "https://webapp3.sallynet.org/api.locator/api/Locations/search/?countToReturn=999&serviceId=0"
all_locations = session.get(all_url).json()

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

for location in all_locations:
    locator_domains.append("https://salvationarmy.ca/")
    page_urls.append("https://salvationarmy.ca/locate")
    location_names.append(location["Name"])
    street_addresses.append(location["Street"])
    citys.append(location["City"])
    states.append(location["ProvinceCode"])
    zips.append(location["Postal"])
    store_numbers.append(location["Id"])
    phones.append(location["Phone"])
    latitudes.append(str(location["Latitude"]))
    longitudes.append(str(location["Longitude"]))
    hours_of_operations.append("<MISSING>")
    if state in canada_state_codes:
        country_codes.append("CA")
    else:
        country_codes.append("<MISSING>")
    location_types.append("<MISSING>")

all_location_df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

all_location_list = all_location_df["store_number"].to_list()
location_types_list = location_types_df["store_number"].to_list()

for store_id in all_location_list:
    if store_id not in location_types_list:
        store_row = all_location_df.loc[all_location_df["store_number"] == store_id]
        location_types_df = location_types_df.append(store_row)

location_types_df = location_types_df.fillna("<MISSING>")
location_types_df = location_types_df.replace(r"^\s*$", "<MISSING>", regex=True)

location_types_df.to_csv("data.csv", index=False)
