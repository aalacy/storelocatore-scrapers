import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
import time
import usaddress


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


session = SgRequests()
driver = SgSelenium().chrome()


def get_value(item):
    if item is None or len(item) == 0:
        item = "<MISSING>"
    return item


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    state = ""
    zipcode = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


all = []


def fetch_data():
    res = session.get("https://kentsgrocery.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    lis = soup.find("ul", {"class": "dropdown-menu"}).find_all("li")

    for li in lis:
        url = "https://kentsgrocery.com" + li.find("a").get("href")
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        store_info_container = soup.find("div", {"id": "storeInfoContain"})
        loc = soup.find("span", {"id": "theStoreName"}).text.strip()
        long, lat = re.findall(
            r"!2d(-?[\d\.]+)!3d(-?[\d\.]+)",
            soup.find("div", {"id": "mapContain"}).find("iframe").get("src"),
        )[0]
        phone = store_info_container.select("a[href*=tel]")[0].text.strip()
        address = (
            store_info_container("h5", text=re.compile(r"Store Address"))[0]
            .find_next("p")
            .get_text(" ")
        )
        store_hour_id = re.findall(r'id="(storeHours[^"]*)"', str(driver.page_source))[
            0
        ]
        tim = store_info_container.find("div", {"id": store_hour_id}).get_text(" ")
        if tim is None or len(tim) == 0:
            tim = "<MISSING>"
        parsed_address = parse_address(address)
        city = loc.replace("Kent's ", "")
        state = parsed_address["state"]
        zipcode = parsed_address["zipcode"]
        street = parsed_address["street"] + parsed_address["city"].replace(city, "")
        all.append(
            [
                "https://kentsgrocery.com",
                loc,
                street,
                city,
                state,
                zipcode,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                url,
            ]
        )
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
