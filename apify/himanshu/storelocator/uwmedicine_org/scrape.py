import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("uwmedicine_org")

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
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    base_url = "https://www.uwmedicine.org"
    links = []
    search_terms = ["s=medicine", "s=liver", "l=98104"]

    for search_term in search_terms:
        base_link = (
            "https://www.uwmedicine.org/search/locations?" + search_term + "&page=0"
        )
        r = session.get(base_link, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        last_page = int(
            (
                soup.find(class_="pager__item pager__item--last")
                .text.strip()
                .split("\n")[1]
            )
        )

        for page in range(0, last_page):
            search_link = (
                "https://www.uwmedicine.org/search/locations?"
                + search_term
                + "&page="
                + str(page)
            )
            logger.info(search_link)
            r = session.get(search_link, headers=headers)
            if r.status_code == 503:
                continue

            soup = BeautifulSoup(r.text, "lxml")
            if soup.find("div", {"class": "clinic-card__street-address"}):
                for link in soup.find_all(
                    "div", {"class": "clinic-card__cta uwm-accent-color__purple"}
                ):
                    if "uwmedicine.org/locations" not in link.find("a")["href"]:
                        continue
                    page_url = link.find("a")["href"]
                    if page_url in links:
                        continue
                    links.append(page_url)
                    r1 = session.get(page_url)
                    soup1 = BeautifulSoup(r1.text, "lxml")

                    try:
                        if (
                            "permanently closed"
                            in soup1.find(class_="clinic-page__hours").text.lower()
                        ):
                            continue
                    except:
                        pass

                    data = json.loads(
                        soup1.find(
                            lambda tag: (tag.name == "script")
                            and '"address"' in str(tag)
                        ).contents[0]
                    )["@graph"][-1]
                    location_name = data["name"]
                    street_address = data["address"]["streetAddress"]

                    digit = re.search(r"\d", street_address).start(0)
                    if digit != 0:
                        street_address = street_address[digit:]

                    city = data["address"]["addressLocality"]
                    state = data["address"]["addressRegion"]
                    zipp = data["address"]["postalCode"]
                    try:
                        phone = data["telephone"]
                    except:
                        phone = "<MISSING>"
                    location_type = "<MISSING>"
                    try:
                        hours = " ".join(
                            list(
                                soup1.find(
                                    "table", {"class": "clinic-page__hours-table"}
                                )
                                .find("tbody")
                                .stripped_strings
                            )
                        )
                    except:
                        if soup1.find("div", {"class": "clinic-page__open-current"}):
                            hours = (
                                soup1.find(
                                    "div", {"class": "clinic-page__open-current"}
                                )
                                .find("span")
                                .text
                            )
                        else:
                            hours = "<MISSING>"
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(
                        street_address.replace("Main Hospital,", "")
                        .replace("West Clinic", "")
                        .replace("East Clinic,", "")
                        .replace("Emergency Department", "")
                        .replace("McMurray Medical Building,", "")
                        .replace(
                            "Center on Human Development and Disability Center,", ""
                        )
                        .strip()
                    )
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append(location_type)
                    store.append("<INACCESSIBLE>")
                    store.append("<INACCESSIBLE>")
                    store.append(hours)
                    store.append(page_url)
                    store = [x.strip() if type(x) == str else x for x in store]
                    if str(store[2]) + str(store[1]) in addresses:
                        continue
                    addresses.append(str(store[2]) + str(store[1]))
                    yield store
            else:
                break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
