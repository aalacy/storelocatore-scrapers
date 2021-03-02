import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("buschs_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    data = []

    base_url = "https://www.buschs.com"
    location_url = "https://www.buschs.com/locations"
    r = session.get(location_url)
    soup = BeautifulSoup(r.text, "html.parser")

    data_list = soup.find("div", {"id": "storelocations"}).findAll(
        "div", {"class": "col-xs-12"}
    )

    for loc in data_list:
        title = loc.find("div", {"class": "panel-heading"}).text
        address_div = loc.find("address")
        street = address_div.find("span", {"class": "street"}).text
        city = address_div.find("span", {"class": "city"}).text.strip(",")
        state = address_div.find("span", {"class": "state"}).text
        zip = address_div.find("span", {"class": "zip"}).text
        hours = address_div.find("span", {"class": "hours"}).text
        phone = address_div.find("a").get("href").strip("tel:")
        storenumber = loc.find("button", {"class": "btn btn-link"})["data-ad"]
        lat_long_list = r.text.split("marker" + storenumber + "")[1].split(") });")[0]
        lat_long_list = lat_long_list.split("new google.maps.LatLng(")[1]
        latitude = lat_long_list.split(", ")[0]
        longitude = lat_long_list.split(", ")[1]

        data.append(
            [
                base_url,
                location_url,
                title,
                street,
                city,
                state,
                zip,
                "US",
                storenumber,
                phone,
                "<MISSING>",
                latitude,
                longitude,
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
