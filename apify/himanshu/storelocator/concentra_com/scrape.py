import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("concentra_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
    base_url = "https://www.concentra.com"

    r = session.get(
        "https://www.concentra.com//sxa/search/results/?s={449ED3CA-26F3-4E6A-BF21-9808B60D936F}|{449ED3CA-26F3-4E6A-BF21-9808B60D936F}&itemid={739CBD3C-A3B6-4CA2-8004-BF6005BB28E9}&v={D907A7FD-050F-4644-92DC-267C1FDE200C}&p=1000"
    ).json()
    for data in r["Results"]:
        page_url = base_url + data["Url"]
        logger.info(page_url)
        location_r = session.get(page_url)
        soup = BeautifulSoup(location_r.text, "lxml")
        try:
            location_name = soup.find("h1", {"class": "field-centername"}).text.strip()
            location_type = location_name.split("-")[-1].strip()
        except:
            location_name = "<MISSING>"
            location_type = "<MISSING>"
        street_address = " ".join(
            list(soup.find("div", {"itemprop": "address"}).stripped_strings)[:-5]
        )
        city = soup.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = soup.find("span", {"itemprop": "addressRegion"}).text.strip()
        zipp = soup.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = soup.find("span", {"itemprop": "telephone"})["content"]
        store_sel = lxml.html.fromstring(location_r.text)
        map_link = "".join(
            store_sel.xpath('//div[@class="static-map"]/img/@data-latlong')
        ).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(map_link) > 0:
            latitude = map_link.split("|")[0].strip()
            longitude = map_link.split("|")[1].strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        hours = store_sel.xpath('//div[@class="hours-container"]/div[1]/div/text()')
        hours_list = []
        for index in range(0, len(hours), 2):
            hours_list.append(hours[index].strip() + ":" + hours[index + 1].strip())

        hours_of_operation = "; ".join(hours_list).strip()
        if len(hours_of_operation) <= 0:
            hours_of_operation = "<MISSING>"

        if len(phone) <= 0:
            phone = "<MISSING>"

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
