import csv
from sgrequests import SgRequests
import time


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []

    session = SgRequests()
    res = session.get(
        "https://www.myhusky.ca/station-locator/json?geo_province=&_=1572547533528",
        verify=False,
    )

    js = res.json()
    time.sleep(1)
    ran = len(js)

    for i in range(ran):
        ids.append(js[i]["station-id"])

        locs.append(js[i]["name"])
        street.append(js[i]["address"])
        cities.append(js[i]["city"])
        states.append(js[i]["province"])
        zips.append(js[i]["postal"])
        phones.append(js[i]["phone"])
        timing.append(js[i]["hours"])
        lati = js[i]["lat"]
        if int(float(lati)) == 0:
            lat.append("<MISSING>")
        else:
            lat.append(lati)
        longi = js[i]["lng"]
        if int(float(longi)) == 0:
            long.append("<MISSING>")
        else:
            long.append(longi)

        ty = js[i]["brand_code"]  # types.append()
        if ty is None or ty == "":
            types.append("<MISSING>")
        else:
            types.append(ty)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.myhusky.ca")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("CA")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(
            "https://www.myhusky.ca/station-locator/json?geo_province=&_=1572547533528"
        )  # page url

        if row not in all:
            all.append(row)

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
