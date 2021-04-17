import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("greyhound_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.greyhound.com",
    "em-api-key": "HeQpRjsFI5xlAaSx2onkjc1HTK0ukqA1IrVvd5fvaMhNtzLTxInTpeYB1MK93pah",
}


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
    url = "https://openair-california.airtrfx.com/hangar-service/v2/ghl/airports/search"
    payload = {
        "outputFields": ["name", "extraInfo", "city", "state", "iataCode"],
        "geoField": {"value": 5000, "name": "geo", "geoFromGeoId": "-942923395"},
        "sortingDetails": [{"field": "geo", "order": "ASC"}],
        "filterFields": [{"name": "active", "values": ["true"]}],
        "setting": {"airportSource": "TRFX", "routeSource": "TRFX"},
        "from": 0,
        "size": 2500,
        "language": "en",
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"name":"' in line:
            items = line.split('{"name":"')
            for item in items:
                if '"city":{' in item:
                    name = item.split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    add = item.split('"street":"')[1].split('"')[0]
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    typ = item.split('"stationStopType":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phoneNumberMain":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    website = "greyhound.com"
                    store = item.split('"iataCode":"')[1].split('"')[0]
                    loc = (
                        "https://www.greyhound.com/en-us/bus-station-"
                        + store
                        + "?redirecturl=true"
                    )
                    state = item.split('"stateAbbreviation":"')[1].split('"')[0]
                    city = item.split('"cityName":"')[1].split('"')[0]
                    country = "US"
                    hrinfo = item.split('"hours":{"hoursBusStation":{')[1].split("}}")[
                        0
                    ]
                    try:
                        hours = (
                            "Sun: "
                            + hrinfo.split('"1":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"1":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = "Sun: Closed"
                    try:
                        hours = (
                            hours
                            + "; Mon: "
                            + hrinfo.split('"2":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"2":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Mon: Closed"
                    try:
                        hours = (
                            hours
                            + "; Tue: "
                            + hrinfo.split('"3":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"3":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Tue: Closed"
                    try:
                        hours = (
                            hours
                            + "; Wed: "
                            + hrinfo.split('"4":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"4":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Wed: Closed"
                    try:
                        hours = (
                            hours
                            + "; Thu: "
                            + hrinfo.split('"5":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"5":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Thu: Closed"
                    try:
                        hours = (
                            hours
                            + "; Fri: "
                            + hrinfo.split('"6":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"6":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Fri: Closed"
                    try:
                        hours = (
                            hours
                            + "; Sat: "
                            + hrinfo.split('"7":[')[1]
                            .split('"open":"')[1]
                            .split('"')[0]
                            + "-"
                            + hrinfo.split('"7":[')[1]
                            .split('"close":"')[1]
                            .split('"')[0]
                        )
                    except:
                        hours = hours + "; Sat: Closed"
                    if phone == "":
                        phone = "<MISSING>"
                    if loc == "":
                        loc = "<MISSING>"
                    if "MEX" not in state and "MEX" not in zc and len(state) == 2:
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
