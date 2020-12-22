import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
}

logger = SgLogSetup().get_logger("zionsbank_com")


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
    url = "https://www.zionsbank.com/locationservices/searchwithfilter"
    payload = {
        "channel": "Online",
        "schemaVersion": "1.0",
        "clientUserId": "ZIONPUBLICSITE",
        "clientApplication": "ZIONPUBLICSITE",
        "transactionId": "txId",
        "affiliate": "0001",
        "searchResults": "2000",
        "username": "ZIONPUBLICSITE",
        "searchAddress": {
            "address": "Salt Lake City, UT",
            "city": "",
            "stateProvince": "",
            "postalCode": "",
            "country": "",
        },
        "distance": "3000",
        "searchFilters": [
            {"fieldId": "1", "domainId": "101", "displayOrder": 1, "groupNumber": 1}
        ],
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "zionsbank.com"
    typ = "Branch"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"locationId":"' in line:
            items = line.split('{"locationId":"')
            for item in items:
                if '"locationName":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"locationName":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"stateProvince":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    lng = item.split('"long":"')[1].split('"')[0]
                    loc = "<MISSING>"
                    try:
                        hours = item.split('"Lobby Hours","value":"')[1].split('"')[0]
                    except:
                        hours = "<MISSING>"
                    if " ATM" not in name:
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
