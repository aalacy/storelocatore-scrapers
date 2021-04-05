import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("picklebarrel_ca")


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
    url = "https://picklebarrel.ca/wp-admin/admin-ajax.php?action=store_search&lat=40.65323&lng=-86.38318&max_results=2500&search_radius=5000&autoload=110"
    r = session.get(url, headers=headers)
    website = "picklebarrel.ca"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        add = item["address"]
        name = item["store"]
        store = item["id"]
        loc = item["permalink"].replace("\\", "")
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        lat = item["lat"]
        lng = item["lng"]
        phone = item["phone"]
        try:
            hours = str(item["hours"])
        except:
            hours = "<MISSING>"
        hours = hours.replace(
            '<table role="presentation" class="wpsl-opening-hours"><tr><td>', ""
        )
        hours = (
            hours.replace("<tr>", "")
            .replace("<td>", "")
            .replace("</tr>", "")
            .replace("</td>", "")
        )
        hours = (
            hours.replace("<time>", ": ")
            .replace("</time></table>", "")
            .replace("</time>", "; ")
        )
        if "None" in hours:
            hours = "<MISSING>"
        name = name.replace("&#038;", "&")
        add = add.replace("&#038;", "&")
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
