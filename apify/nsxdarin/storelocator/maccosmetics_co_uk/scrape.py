import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("maccosmetics_co_uk")


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
    url = "https://www.maccosmetics.co.uk/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents"
    payload = {
        "JSONRPC": '[{"method":"locator.doorsandevents","id":2,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, SUB_HEADING, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE, COMMENTS","country":"United States","latitude":51.5073509,"longitude":-0.1277583,"radius":2500,"region_id":"1"}]}]'
    }
    r = session.post(url, headers=headers, data=payload)
    website = "maccosmetics.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"DOOR_ID":' in line:
            items = line.split('"DOOR_ID":')
            for item in items:
                if '"STORE_TYPE":"' in item:
                    store = item.split('"')[0]
                    typ = item.split('"STORE_TYPE":"')[1].split('"')[0]
                    loc = "<MISSING>"
                    city = item.split('"CITY":"')[1].split('"')[0]
                    name = item.split('"DOORNAME":"')[1].split('"')[0]
                    phone = item.split('"PHONE1":"')[1].split('"')[0]
                    lat = item.split('"LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"LONGITUDE":"')[1].split('"')[0]
                    add = (
                        item.split('"ADDRESS":"')[1].split('"')[0]
                        + " "
                        + item.split('"ADDRESS2":"')[1].split('"')[0]
                    )
                    add = add.strip()
                    zc = item.split('"ZIP_OR_POSTAL":"')[1].split('"')[0]
                    state = item.split('STATE_OR_PROVINCE":"')[1].split('"')[0]
                    if state == "":
                        state = "<MISSING>"
                    hours = item.split('{"hours":"')[1].split('"')[0]
                    if phone == "":
                        phone = "<MISSING>"
                    if typ == "":
                        typ = "MAC"
                    if "once again putting" in hours:
                        hours = "Temporarily Closed"
                    if "contact this store" in hours.lower():
                        hours = "<MISSING>"
                    if "Boots" not in name and state != "Ireland":
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
