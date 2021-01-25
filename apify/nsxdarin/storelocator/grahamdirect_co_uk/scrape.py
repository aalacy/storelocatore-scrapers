import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("grahamdirect_co_uk")


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
    ids = []
    website = "grahamdirect.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    for x in range(48, 60):
        url = (
            "https://www.grahamdirect.co.uk/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(x)
            + "&lng=-0.12776&max_results=100&search_radius=500"
        )
        logger.info("Pulling Stores")
        r = session.get(url, headers=headers)
        for item in json.loads(r.content):
            name = item["store"].replace("&#8211;", "-").replace("&#8217;", "")
            add = item["address"]
            store = item["id"]
            add = add + " " + item["address2"]
            add = add.strip()
            city = item["city"]
            state = "<MISSING>"
            zc = item["zip"]
            lat = item["lat"]
            lng = item["lng"]
            phone = item["phone"]
            hours = item["hours"]
            hours = hours.replace(
                '<table role="presentation" class="wpsl-opening-hours"><tr><td>', ""
            )
            hours = hours.replace("</td></tr></table>", "")
            hours = hours.replace("</td><td><time>", ": ").replace(
                "</time></td></tr><tr><td>", "; "
            )
            hours = hours.replace("</td><td>Closed", ": Closed").replace(
                "</td></tr><tr><td>", "; "
            )
            if store not in ids:
                ids.append(store)
                if lat == "55.962371":
                    city = "Edinburgh"
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
