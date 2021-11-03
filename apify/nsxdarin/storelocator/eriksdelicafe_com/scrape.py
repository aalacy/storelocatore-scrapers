import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("eriksdelicafe_com")


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
    url = "https://eriksdelicafe.com/wp-admin/admin-ajax.php?action=store_search&lat=36.97412&lng=-122.0308&max_results=500&search_radius=5000&autoload=1"
    r = session.get(url, headers=headers)
    website = "eriksdelicafe.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["id"]
        add = item["address"]
        name = item["store"].replace("\\", "")
        add = add + " " + item["address2"]
        add = add.strip()
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        lat = item["lat"]
        lng = item["lng"]
        phone = item["phone"]
        loc = "https://eriksdelicafe.com" + item["url"].replace("\\", "")
        hours = str(item["hours"])
        hours = hours.replace(
            '<table role="presentation" class="wpsl-opening-hours"><tr><td>', ""
        )
        hours = hours.replace("</time></td></tr><tr><td>", "; ")
        hours = hours.replace("</td><td><time>", ": ")
        hours = hours.replace("</time></td></tr></table>", "")
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
