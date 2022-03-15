import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("firstusbank_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=100,
    max_search_results=15,
)


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    store_types = ["branches", "atms"]
    for lat, lng in search:
        for types in store_types:
            url = "https://www.fusb.com/_/api/{types}/{lat}/{lng}/250".format(
                lat=lat, lng=lng, types=types
            )
            stores_req = session.get(url, headers=headers).json()
            if types == "atms":
                stores_req = stores_req["atms"]
            else:
                stores_req = stores_req["branches"]
            for store in stores_req:
                title = store["name"]
                street = store["address"]
                city = store["city"]
                state = store["state"]
                pcode = store["zip"]
                lat = store["lat"]
                lng = store["long"]
                if types == "branches":
                    phone = store["phone"].strip()
                    raw_hours = store["description"].strip()
                    raw_hours = raw_hours.replace(
                        '<div><span style="font-weight: 600;">Lobby &amp; Drive Thru Hours:&nbsp;</span></div><div>',
                        "",
                    )
                    raw_hours = raw_hours.replace("</div><div>", " ")
                    raw_hours = raw_hours.replace(
                        "<div><b>Lobby &amp; Drive Thru Hours:&nbsp;</b> ", ""
                    )
                    raw_hours = raw_hours.replace("<br>", "")
                    raw_hours = raw_hours.replace(
                        "<div><b>Lobby &amp; Drive Thru Hours:</b>&nbsp; ", ""
                    )
                    hours = raw_hours.replace("</div>", "").strip()
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                else:
                    phone = "<MISSING>"
                    hours = "<MISSING>"
                if street == "100W.EmoryRoad":
                    street = "100W. Emory Road"
                if street == "8710Highway69South":
                    street = "8710 Highway 69 South"
                if street == "2619UniversityBlvd":
                    street = "2619 University Blvd"
                data.append(
                    [
                        "https://www.fusb.com/",
                        "https://www.fusb.com/resources/locations",
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        phone,
                        types,
                        lat,
                        lng,
                        hours,
                    ]
                )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
