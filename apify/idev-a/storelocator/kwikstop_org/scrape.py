import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json

from util import Util  # noqa: I900

myutil = Util()


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


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "if-none-match": 'W/"bcfa8c7dc75755d3df09551e3b52e458--gzip"',
        "cookie": "ss_cid=9bd93a77-b623-4816-a67d-52a776ef0246; crumb=BfDvKQnjKxSiNjBkZDJjMWRhN2U3ZGY0ZGQ0MDRlYzZiMDM5M2Ew; ss_cvr=f8fe2f59-117b-4ce7-962f-94b81bdf8552|1612172609433|1612225117773|1612456979363|7; ss_cvt=1612456979363; ss_cvisit=1612456980517; ss_cpvisit=1612456980517",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def fetch_data():
    data = []

    locator_domain = "https://www.kwikstop.org/"
    base_url = "https://www.kwikstop.org/locations"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("#page .row.sqs-row a")
    for link in links:
        page_url = urljoin(
            "https://www.kwikstop.org",
            f"{link['href']}",
        )
        r1 = session.get(page_url, headers=_headers())
        soup1 = bs(r1.text, "lxml")
        rows = soup1.select("#page .row.sqs-row .row.sqs-row")
        for row in rows:
            map_blocks = row.select(".sqs-block-map")
            html_blocks = row.select(".sqs-block-html")
            for x in range(len(map_blocks)):
                location = map_blocks[x]
                if location:
                    location1 = [_ for _ in html_blocks[x].stripped_strings]
                    block = json.loads(location["data-block-json"])["location"]
                    location_name = location1[0].split("#")[0].strip()
                    store_number = location1[0].split("#")[1].strip()
                    street_address = location1[1]
                    address = location1[2].split(",")
                    city = address[0]
                    state = ""
                    zip = ""
                    if len(address) == 2:
                        state = (
                            address[1].strip().split(" ")[0].replace(".", "").strip()
                        )
                        zip = address[1].strip().split(" ")[1].replace(",", "").strip()
                    else:
                        zip = address[-1].strip().replace(".", "").strip()
                        state = address[1].strip().replace(",", "").strip()

                    country_code = "US"
                    phone = myutil._valid(location1[-1].replace("Phone:", ""))
                    location_type = "<MISSING>"
                    latitude = block["mapLat"]
                    longitude = block["mapLng"]
                    hours_of_operation = "<MISSING>"

                    _item = [
                        locator_domain,
                        page_url,
                        location_name,
                        street_address,
                        city,
                        state,
                        zip,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation,
                    ]

                    data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
