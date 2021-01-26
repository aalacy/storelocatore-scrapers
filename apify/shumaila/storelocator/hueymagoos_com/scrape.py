import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("brakecheck_com")


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
    base_url = "https://code.metalocator.com/index.php?option=com_locator&view=directory&force_link=1&tmpl=component&task=search_zip&framed=1&format=raw&no_html=1&templ[]=address_format&layout=_jsonfast&postal_code=40.7128,-74.006&radius=5000&interface_revision=266&limitstart=0&limit=500&user_lat=0&user_lng=0&Itemid=10475&preview=0&parent_table=&parent_id=0&search_type=point&_opt_out=&ml_location_override=&reset=false&nearest=true&national=false&callback=handleJSONPResults"
    r = session.get(base_url, headers=headers)
    data_list = r.text.split('"results":')[1].split("}]", 1)[0] + "}]"
    data_list = json.loads(data_list)
    print(len(data_list))

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
