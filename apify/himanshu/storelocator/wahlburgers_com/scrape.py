import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

session = SgRequests()

log = SgLogSetup().get_logger("wahlburgers.com")


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


def fetch_data():
    base_url = "https://wahlburgers.com"
    r = session.get(base_url + "/all-locations")
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    us_main = (
        soup.find("section", {"id": "body"})
        .find("div", {"class": "locations"})
        .find("div", {"class": "us"})
        .find_all("a")
    )
    other_main = (
        soup.find("section", {"id": "body"})
        .find("div", {"class": "locations"})
        .find("div", {"class": "other"})
        .find_all("a")
    )
    all_links = []
    for atag in us_main:
        country = "US"
        link = base_url + atag["href"]
        all_links.append([link, country])
    for atag in other_main:
        link = base_url + atag["href"]
        if "canada" in link:
            country = "CA"
            all_links.append([link, country])
        elif "uk" in link:
            country = "UK"
            all_links.append([link, country])
        else:
            continue
    all_links.append(["https://wahlburgers.com/all-locations/uk", "UK"])

    found = []
    for i in all_links:
        link = i[0]
        country = i[1]

        if link not in found:
            log.info(link)
            found.append(link)
            r1 = session.get(link)
            soup1 = BeautifulSoup(r1.text, "lxml")
            main1 = (
                soup1.find("section", {"id": "body"})
                .find("div", {"class": "locationset"})
                .find("div", {"class": "cell"})
                .find_all("a", {"class": "fadey"})
            )
            for i, atag1 in enumerate(main1):
                try:
                    fin_link = base_url + atag1["href"]
                    if fin_link == "https://wahlburgers.com":
                        continue
                    if fin_link in found:
                        continue
                    found.append(fin_link)
                    r2 = session.get(fin_link)
                    got_page = True
                except:
                    got_page = False

                if got_page:
                    soup2 = BeautifulSoup(r2.text, "lxml")
                    if (
                        soup2.find("script", {"type": "application/ld+json"})
                        is not None
                    ):
                        loc = json.loads(
                            soup2.find("script", {"type": "application/ld+json"}).text,
                            strict=False,
                        )
                        store = []
                        hour = " ".join(loc["openingHours"]).strip()
                        lt = soup2.find(
                            "div", {"class": "responsive-embed widescreen"}
                        ).find("iframe")["src"]
                        lng = lt.split("!2d")[1].split("!3d")[0]
                        lat = lt.split("!3d")[1].split("!")[0]
                        if (
                            len(
                                soup2.find("div", {"class": "insideThing"}).find_all(
                                    "div"
                                )
                            )
                            > 4
                        ):
                            zip = (
                                list(
                                    soup2.find("div", {"class": "insideThing"})
                                    .find_all("div")[2]
                                    .stripped_strings
                                )[-1]
                                .split("\n")[-1]
                                .strip()
                            )
                        else:
                            zip = (
                                list(
                                    soup2.find("div", {"class": "insideThing"})
                                    .find_all("div")[1]
                                    .stripped_strings
                                )[-1]
                                .split("\n")[-1]
                                .strip()
                            )
                        if len(zip) != 5:
                            zip = (
                                list(
                                    soup2.find("div", {"class": "insideThing"})
                                    .find_all("div")[2]
                                    .stripped_strings
                                )[-1]
                                .split("\n")[-1]
                                .strip()
                            )
                        if (
                            zip
                            == "Sun-Mon: 5am-10pm subject to departing flight schedules"
                        ):
                            zip = "L5P 1B2"
                        store.append(base_url)
                        store.append(
                            loc["name"]
                            .strip()
                            .lstrip()
                            .rstrip()
                            .replace("\n", "")
                            .replace("\t", "")
                            .replace("\n ", " ")
                            .replace("  ", " ")
                        )
                        street_address = loc["address"]["streetAddress"].strip()
                        digit = re.search(r"\d", street_address).start(0)
                        if digit != 0:
                            street_address = street_address[digit:]
                        store.append(street_address)
                        store.append(loc["address"]["addressLocality"].strip())
                        store.append(loc["address"]["addressRegion"].strip())
                        store.append(zip)
                        store.append(country)
                        store.append("<MISSING>")
                        if loc["telephone"]:
                            store.append(loc["telephone"])
                        else:
                            store.append("<MISSING>")
                        if "Temporarily" in str(main1[i]):
                            loc_type = "Temporarily Closed"
                        else:
                            loc_type = "Open"
                        store.append(loc_type)
                        store.append(lat)
                        store.append(lng)
                        if hour:
                            store.append(hour)
                        else:
                            store.append("<MISSING>")
                        store.append(fin_link)
                        if "66877" in zip:
                            continue
                        return_main_object.append(store)
                else:
                    store = []
                    raw_address = list(
                        (
                            soup1.find("section", {"id": "body"})
                            .find("div", {"class": "locationset"})
                            .find("div", {"class": "cell"})
                            .find_all("p")[1:]
                        )[i].stripped_strings
                    )
                    street_address = raw_address[0]
                    city = raw_address[1].split(",")[0]
                    state = "<MISSING>"
                    zip_code = raw_address[1].split(",")[1].replace("UK", "").strip()
                    if "Temporarily" in str(main1[i]):
                        loc_type = "Temporarily Closed"
                    else:
                        loc_type = "Open"
                    hour = "<MISSING>"
                    store.append(base_url)
                    store.append(main1[i].h2.text)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zip_code)
                    store.append(country)
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(loc_type)
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(hour)
                    store.append(link)
                    return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
