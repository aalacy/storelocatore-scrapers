import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("bradlygas_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    data = []
    base_url = "https://www.bradleygas.com/wp-content/plugins/store-locator/sl-xml.php"
    r = session.get(base_url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("marker")
    for loc in data_list:
        title = loc["name"].replace("&amp", "and")
        title = re.sub(r"[()\#/@;:<>{}`+=~|.!?,]", "", title)

        street = loc["street"]
        lat = loc["lat"]
        lng = loc["lng"]
        phone = loc["phone"]
        city = loc["city"]
        state = loc["state"]
        zip = loc["zip"]
        storenum = loc["description"].replace("#", "").replace("-", "")
        if loc["hours"]:
            hours_of_operation = loc["hours"]
        else:
            hours_of_operation = "<MISSING>"
        data.append(
            [
                "www.bradleygas.com",
                "https://www.bradleygas.com/locations/",
                title,
                street,
                city,
                state,
                zip,
                "US",
                storenum,
                phone,
                "<MISSING>",
                lat,
                lng,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
