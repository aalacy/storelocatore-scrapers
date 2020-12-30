import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("brakesplus_com")


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
    url = "https://www.brakesplus.com/wp/wp-admin/admin-ajax.php"
    payload = {
        "address": "",
        "formdata": "addressInput=",
        "lat": "37.09024",
        "lng": "-95.712891",
        "name": "",
        "options[initial_radius]": "10000",
        "options[initial_results_returned]": "200",
        "action": "csl_ajax_onload",
        "radius": "10000",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "brakesplus.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"name":"' in line:
            items = line.split('"name":"')
            for item in items:
                if '"address":"' in item:
                    name = item.split('"')[0]
                    store = item.split('"id":"')[1].split('"')[0]
                    add = item.split(',"address":"')[1].split('"')[0]
                    state = item.split(',"state":"')[1].split('"')[0]
                    city = item.split(',"city":"')[1].split('"')[0]
                    zc = item.split(',"zip":"')[1].split('"')[0]
                    lat = item.split(',"lat":"')[1].split('"')[0]
                    lng = item.split(',"lng":"')[1].split('"')[0]
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    hours = item.split(',"hours":"')[1].split('"')[0]
                    hours = hours.replace("\\r\\n", "; ")
                    if phone == "":
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
