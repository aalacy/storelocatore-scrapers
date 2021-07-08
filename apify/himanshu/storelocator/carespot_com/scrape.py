import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carespot_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    data = "action=locations-get_map_locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded",
    }
    r = session.post(
        "https://www.carespot.com/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    return_main_object = []
    for location in r.json()["data"]:
        page_url = BeautifulSoup(location["info"], "lxml").find("a")["href"]

        location_type = page_url.split("/")[-3].strip().replace("-", " ").capitalize()
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        if (
            location_soup.find("p", text=re.compile("coming soon!", re.IGNORECASE))
            is not None
        ):
            continue
        try:
            address = location_soup.find("span", {"itemprop": "streetAddress"}).text
            city = location_soup.find("span", {"itemprop": "addressLocality"}).text
            state = location_soup.find("span", {"itemprop": "addressRegion"}).text
            zip_code = location_soup.find("span", {"itemprop": "postalCode"}).text
        except:
            continue
        try:
            phone = location_soup.find("span", {"itemprop": "telephone"}).text
        except:
            phone = "<MISSING>"
        if location_soup.find("div", {"class": "hours"}) is None:
            location_hours = "<MISSING>"
        else:
            location_hours = " ".join(
                list(location_soup.find("div", {"class": "hours"}).stripped_strings)
            ).replace("Location Hours", "")
        try:
            cms = BeautifulSoup(location["info"], "lxml").find("h4").text
        except:
            cms = "<MISSING>"
        if "Coming Soon!" in cms:
            location_hours = "Coming Soon"
        store = []
        store.append("https://www.carespot.com")
        store.append(
            "".join(location["title"]).replace("&#8211;", "–").replace("&amp;", "&")
        )
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append("US")
        store.append(location["id"])
        store.append(phone if phone != "" else "<MISSING>")
        store.append(location_type)
        store.append(location["lat"])
        store.append(location["lng"])
        store.append(location_hours if location_hours != "" else "<MISSING>")
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
