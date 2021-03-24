from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from lxml import html
import csv
import re

logger = SgLogSetup().get_logger("kmart_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
}
DOMAIN = "https://www.kmart.com/"


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
    # Your scraper here
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.kmart.com/stores.html/"
    r_base = session.get(url, headers=headers)
    r_base_data = html.fromstring(r_base.text, "lxml")
    logger.info("crawling from base url:%s" % url)
    state_list = r_base_data.xpath('//*[@id="stateList"]/li/ul/li/a/@href')
    p = 0
    for statenow in state_list:
        statenow = "https://www.kmart.com" + statenow
        r_state = session.get(statenow, headers=headers)
        r_state_data = html.fromstring(r_state.text, "lxml")
        try:
            link_list = r_state_data.xpath('//*[@id="cityList"]/div/ul/li/a/@href')
        except:
            continue
        for url_store in link_list:
            url_store = "https://www.kmart.com" + url_store
            logger.info("Pulling the data from: %s" % url_store)
            r = session.get(url_store, headers=headers)
            locator_domain = DOMAIN
            page_url = url_store or "<MISSING>"
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("small", {"itemprop": "name"}).text
            title = (
                title.replace("Kmart", "Kmart ").replace("#", " # ").replace("  ", " ")
            )
            title = title.replace("\xa0", "").replace("\t", "").replace("\n", "")
            location_name = title or "<MISSING>"
            street_address = (
                r.text.split("address", 1)[1].split('"', 1)[1].split('"', 1)[0]
            )
            city = r.text.split("city", 1)[1].split('"', 1)[1].split('"', 1)[0]
            state = r.text.split("state = ", 1)[1].split('"', 1)[1].split('"', 1)[0]
            zip = r.text.split("zip = ", 1)[1].split('"', 1)[1].split('"', 1)[0]
            country_code = "US" or "<MISSING>"
            store_number = (
                r.text.split("unitNumber", 1)[1].split("= ", 1)[1].split(",", 1)[0]
            )
            store_number = store_number.replace('"', "") or "<MISSING>"
            phone = r.text.split("phone", 1)[1].split('"', 1)[1].split('"', 1)[0]
            location_type = "<MISSING>"
            latitude = r.text.split("lat = ", 1)[1].split(",", 1)[0]
            longitude = r.text.split("lon = ", 1)[1].split(",", 1)[0]
            hoo = soup.text.split("Hours")[1].split("Holiday", 1)[0]
            hoo = re.sub(pattern, "", hoo).replace("pm", "pm ").replace("\n", " ")
            hoo = hoo.replace("day", "day ").replace("  ", " ")
            try:
                hours_of_operation = hoo.split("In-Store", 1)[0]
            except:
                pass
            try:
                hours_of_operation = hoo.split("Nearby", 1)[0]
            except:
                pass

            data.append(
                [
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
            )
            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
