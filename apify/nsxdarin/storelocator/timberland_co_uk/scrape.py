import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("timberland_co_uk")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch?like=0.9297644562205771&lang=en_US"
    payload = {
        "request": {
            "appkey": "2047B914-DD9C-3B95-87F3-7B461F779AEB",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "atleast": 1,
                "limit": 250,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "Liverpool",
                            "country": "UK",
                            "latitude": 53.4083714,
                            "longitude": -2.9915726,
                            "state": "",
                            "province": "Merseyside",
                            "city": "Liverpool",
                            "address1": "",
                            "postalcode": "",
                        }
                    ]
                },
                "searchradius": "1000",
                "radiusuom": "km",
                "order": "retail_store,outletstore,authorized_reseller,_distance",
                "where": {
                    "or": {
                        "retail_store": {"eq": ""},
                        "outletstore": {"eq": ""},
                        "icon": {"eq": ""},
                    },
                    "and": {
                        "service_giftcard": {"eq": ""},
                        "service_clickcollect": {"eq": ""},
                        "service_secondchance": {"eq": ""},
                        "service_appointment": {"eq": ""},
                        "service_reserve": {"eq": ""},
                        "service_onlinereturns": {"eq": ""},
                        "service_orderpickup": {"eq": ""},
                        "service_virtualqueuing": {"eq": ""},
                        "service_socialpage": {"eq": ""},
                        "service_eventbrite": {"eq": ""},
                        "service_storeevents": {"eq": ""},
                        "service_whatsapp": {"eq": ""},
                    },
                },
                "false": "0",
            },
        }
    }

    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "timberland.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["response"]["collection"]:
        phone = item["phone"]
        store = "<MISSING>"
        add = (
            str(item["address1"])
            + " "
            + str(item["address2"])
            + " "
            + str(item["address3"])
        )
        add = add.strip()
        city = item["city"]
        state = item["province"]
        zc = item["postalcode"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        cty = item["country"]
        name = name.replace("&reg;", "").replace("  ", " ").replace("  ", " ")
        hours = "<MISSING>"
        if state == "" or state is None:
            state = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if cty == "UK":
            if "Outlet" in name:
                typ = "Timberland Outlet Store"
            else:
                typ = "Timberland Store"
            if "TBC" in phone:
                phone = "<MISSING>"
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
