from sgrequests import SgRequests
import re
import pandas as pd

session = SgRequests()

url = "https://graphql.contentful.com/content/v1/spaces/13n1l6os99jz/"

headers = {"authorization": "Bearer BlDmgl7JtKeJ-tRqK8y-Nxt5Q7bjpRiJUb6aL2vHw8U"}
params = {
    "query": '        query storeCollection {            storeCollection(skip: 0, limit: 1000, where:{AND: [{type: "Drybar Shop"}]}) {                items {                    title                    number                    bookerLocationId                    type                    information                    contact                    slug                    settings                    arrivalInformation                }            }        }    '
}

response = session.post(url, headers=headers, data=params).json()

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

for location in response["data"]["storeCollection"]["items"]:
    try:
        status = location["settings"]["operatingStatus"]
        if "coming" in status.lower():
            continue
    except KeyError:
        pass
    locator_domain = "thedrybar.com"
    page_url = "https://www.drybarshops.com/service/locator"
    location_name = location["title"]
    address = location["contact"]["street1"]
    city = location["contact"]["city"]
    state = location["contact"]["state"]
    zipp = location["contact"]["postalCode"]
    try:
        if int(zipp) > 99999 and len(zipp) > 5:
            zipp = "<MISSING>"
    except Exception:
        pass

    try:
        country_code = location["contact"]["country"]
        if state == "CA":
            country_code = "US"
    except Exception:
        country_code = "US"

    store_number = location["bookerLocationId"]
    try:
        phone = location["contact"]["phoneNumber"]
    except Exception:
        phone = "<MISSING>"

    if location["settings"]["operatingStatus"] == "CLOSED_TEMPORARILY":
        location_type = location["settings"]["operatingStatus"]
    else:
        location_type = location["type"]

    latitude = location["contact"]["coordinates"][0]
    longitude = location["contact"]["coordinates"][1]

    hours = ""
    for item in location["settings"]["operatingHours"]:
        if bool(re.search(r"\d", item[0])) is True:
            continue

        day = item[0]
        time = item[1]
        hours = hours + day + "-" + time + ", "

    hours = hours[:-2]

    locator_domains.append(locator_domain)
    page_urls.append(page_url)
    location_names.append(location_name)
    street_addresses.append(address)
    citys.append(city)
    states.append(state)
    zips.append(zipp)
    country_codes.append(country_code)
    store_numbers.append(store_number)
    phones.append(phone)
    location_types.append(location_type)
    latitudes.append(latitude)
    longitudes.append(longitude)
    hours_of_operations.append(hours)


df = pd.DataFrame(
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

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
