import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

log = sglog.SgLogSetup().get_logger(logger_name="eurekarestaurantgroup.com")
session = SgRequests()

base_url = "https://eurekarestaurantgroup.com"


def write_output(data):
    with open("data.csv", newline="", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    soup = BeautifulSoup(
        session.get("https://eurekarestaurantgroup.com/locations").text, "lxml"
    )
    for url in soup.find("section", {"id": "content"}).find_all("a"):
        page_url = url["href"]
        log.info(page_url)
        store_resp = session.get(page_url).text
        store_sel = lxml.html.fromstring(store_resp)
        location_soup = BeautifulSoup(store_resp, "lxml")

        location_name = "".join(
            store_sel.xpath('//h1[@data-yext-field="locationName"]/text()')
        ).strip()
        addr = list(
            location_soup.find("div", {"class": "col-sm-3 padding-0"})
            .find("p")
            .stripped_strings
        )
        street_address = addr[0]
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[-1].split()[0]
        zipp = addr[1].split(",")[-1].split()[-1]

        phone = "".join(store_sel.xpath('//a[contains(@href,"tel:")]/text()')).strip()
        if phone == "":
            phone = "<MISSING>"

        temp_hours = store_sel.xpath('//p[@class="hours-large"]')
        hours_list = []
        for hour in temp_hours:
            hours_list.append(
                "".join(hour.xpath("text()"))
                .strip()
                .replace("\n", ":")
                .strip()
                .replace("    ", "")
                .strip()
                .replace(" :", ": ")
                .replace("to", " to")
                .strip()
            )

        hours = "; ".join(hours_list).strip()
        if "Opens" in hours:
            continue

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "maps/place" in store_resp:
            map_link = store_resp.split("maps/place")[1].strip().split('"')[0].strip()
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

        output = []
        output.append(base_url)  # url
        output.append(location_name)  # location name
        output.append(street_address)  # address
        output.append(city)  # city
        output.append(state)  # state
        output.append(zipp)  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        output.append(phone)  # phone
        output.append("Restaurants")  # location type
        output.append(latitude)  # latitude
        output.append(longitude)  # longitude
        output.append(hours)  # opening hours
        output.append(page_url)
        yield output


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
