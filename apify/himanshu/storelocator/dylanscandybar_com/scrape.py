import csv
from lxml import etree
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dylanscandybar_com")


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
    session = SgRequests()
    r = session.get("https://www.dylanscandybar.com/pages/visit")
    soup = bs(r.text, "lxml")
    data = soup.find_all(
        "div", {"class": "map-section-content-wrapper desktop-3 tablet-2 mobile-3"}
    )
    for i in data:
        add = list(i.stripped_strings)[-2].split(",")
        if "Phase IV" in add or "127 S. Ocean Road" in add:
            continue
        if "Canada" in add[-1]:
            del add[-1]
        name = " ".join(list(i.find("h2").stripped_strings))
        phone = "<MISSING>"
        hoo_html = etree.HTML(str(i))
        hoo = hoo_html.xpath('.//p[strong[contains(text(), "Hours:")]]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(i.text)
        )
        if phone_list:
            phone = phone_list[-1]
        closed = i.select_one('strong:contains("Closed due to the COVID-19")')
        location_type = "<MISSING>"
        if closed:
            location_type = "closed"
        state = add[-1].strip().split()[0].replace("New", "NY")
        zipp = (
            " ".join(add[-1].strip().split()[1:])
            .replace(" - Terminal B", "")
            .replace("York ", "")
        )
        city = (
            add[-2]
            .replace("11000 Terminal Access Rd.", "")
            .replace("6301 Silver Dart Dr", "")
            .replace("Space #SR2", "")
            .strip()
        )
        street_address = (
            " ".join(add)
            .replace(state, "")
            .replace(zipp, "")
            .replace(city, "")
            .replace(",", " ")
            .replace("      ", "")
        )

        lat = "<MISSING>"
        lng = "<MISSING>"
        store = []
        store.append("https://www.dylanscandybar.com/")
        store.append(name.replace("|", "").strip())
        store.append(street_address.strip().replace("- Terminal B", ""))
        store.append(city.strip())
        store.append(state.strip())
        store.append(zipp)
        if "6301 Silver Dart Dr" in street_address:
            store.append("CA")
        else:

            store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(lat.strip() if lat.strip() else "<MISSING>")
        store.append(lng.strip() if lng.strip() else "<MISSING>")
        store.append(hours_of_operation)
        store.append("<MISSING>")
        store = [
            x.encode("ascii", "ignore").decode("ascii").strip() if type(x) == str else x
            for x in store
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
