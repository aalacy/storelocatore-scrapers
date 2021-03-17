import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://elevatetrampolinepark.com/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for location in soup.find_all(
        "a", {"class": re.compile(r"et_pb_button et_pb_button_.+")}
    ):
        link = location["href"]
        location_request = session.get(link)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        if location_soup.find("h4") is None:
            continue
        name = location_soup.title.text.replace(
            "is the premier extreme recreation park!", ""
        ).strip()
        if location_soup.find("div", {"class": "textwidget"}) is None:
            continue
        location_address = list(
            location_soup.find("div", {"class": "textwidget"}).stripped_strings
        )
        phone = location_soup.find(class_="phone").text.strip()
        try:
            geo_location = location_soup.find(
                "iframe", {"data-src": re.compile("/maps/")}
            )["data-src"]
        except:
            geo_location = location_soup.find("iframe", {"src": re.compile("/maps/")})[
                "src"
            ]
        hours = list(
            location_soup.find_all("div", {"class": "textwidget"})[-1].stripped_strings
        )
        store = []
        store.append("https://elevatetrampolinepark.com")
        store.append(link)
        store.append(name)
        store.append(location_address[0])
        store.append(location_address[1].split(",")[0])
        store.append(location_address[1].split(" ")[-2])
        store.append(location_address[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(" ".join(hours).replace("–", "-"))
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    scrape()
