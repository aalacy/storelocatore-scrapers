import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("expstores_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://expstores.com/"
    soup = bs(session.get(base_url).content, "lxml")
    headers = {
        "accept": "text/html, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    for url in soup.find_all("a", {"class": re.compile("mpfy-pin mpfy-pin-id-")}):

        store_number = url["data-id"]
        page_url = url["href"]
        logger.info(page_url)
        store_req = session.get(page_url, headers=headers)
        location_soup = bs(store_req.content, "lxml")
        store_sel = lxml.html.fromstring(store_req.text)
        addr = store_sel.xpath('//div[@class="mpfy-location-details"]/div/p/text()')
        add_list = []
        for add in addr:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city_state_zip = add_list[1].strip()
        state = city_state_zip.split(" ", 1)[0].strip()
        zipp = city_state_zip.rsplit(" ", 1)[-1].strip()
        city = city_state_zip.replace(state, "").replace(zipp, "").strip()
        phone = add_list[3].strip()
        country_code = add_list[2].strip()
        location_name = location_soup.find("div", {"class": "mpfy-title"}).text
        coords = location_soup.find(
            "a", {"class": "mpfy-p-bg-gray mpfy-p-color-accent-background"}
        )["href"]
        lat = coords.split("=")[-1].split(",")[0]
        lng = coords.split("=")[-1].split(",")[1]

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
