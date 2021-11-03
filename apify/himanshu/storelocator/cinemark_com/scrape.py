import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("cinemark_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w") as output_file:
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
    base_url = "https://cinemark.com/"

    r = session.get("https://cinemark.com/full-theatre-list")

    stores_sel = lxml.html.fromstring(r.text)
    links = stores_sel.xpath('//div[@class="columnList wide"]//a/@href')
    for link in links:
        page_url = "https://cinemark.com/" + link
        logger.info(page_url)
        r1 = session.get(page_url)
        store_sel = lxml.html.fromstring(r1.text)
        info = "".join(
            store_sel.xpath('//script[@type="application/ld+json"]/text()')
        ).strip()

        try:
            data = json.loads(info)
            for address in data["address"]:
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zipp = address["postalCode"]
                country_code = address["addressCountry"]
            phone = data["telephone"]
            location_name = data["name"]
            if "NOW CLOSED".lower() in location_name.lower():
                continue
            location_type = data["@type"]
            latitude = (
                "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
                .split("pp=")[1]
                .split(",")[0]
            )
            longitude = (
                "".join(store_sel.xpath('//div[@class="theatreMap"]/a/img/@data-src'))
                .split("pp=")[1]
                .split(",")[1]
                .split("&")[0]
            )

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url)

            yield store
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
