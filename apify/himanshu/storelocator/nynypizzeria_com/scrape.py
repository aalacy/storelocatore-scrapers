import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://nynypizzeria.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for div in soup.find("div", {"class": "middle_inner"}).find_all(
        "div", recursive=False
    ):
        if div.find("h1") is None:
            continue
        if div.find_next_sibling("div").find("iframe") is None:
            continue
        name = div.find("h1").text.strip()
        geo_request = session.get(
            div.find_next_sibling("div").find("iframe")["src"], headers=headers
        )
        geo_soup = BeautifulSoup(geo_request.text, "lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in str(script):
                geo_data = json.loads(
                    script.contents[0].split("initEmbed(")[1].split(");")[0]
                )[21][3][0][1]
                lat = json.loads(str(script).split("initEmbed(")[1].split(");")[0])[21][
                    3
                ][0][2][0]
                lng = json.loads(str(script).split("initEmbed(")[1].split(");")[0])[21][
                    3
                ][0][2][1]
                break
        street_address = geo_data.split(",")[1].strip()
        city = geo_data.split(",")[2].strip()
        store_zip_split = re.findall(
            re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), geo_data
        )
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        state_split = re.findall("([A-Z]{2})", geo_data)
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"

        if "Airside" in city:
            street_address = street_address + "-" + city
            city = "Tampa"

        try:
            phone = (
                div.find_next_sibling("div")
                .find("a", {"href": re.compile("tel:")})["href"]
                .replace("tel:", "")
            )
        except:
            phone = "<MISSING>"

        store = []
        store.append("https://nynypizzeria.com")
        store.append(name.strip())
        store.append(street_address.strip())
        store.append(city.strip())
        store.append(state.strip())
        store.append(store_zip.strip())
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append("https://nynypizzeria.com/locations")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
