import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "http://quicklyusa.com"

    urls = [
        "http://quicklyusa.com/quicklystores.html",
        "http://quicklyusa.com/otqulo.html",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        for location in soup.find_all("table")[2].find_all("a"):
            if location.text == "":
                continue
            page_url = base_url + "/" + location["href"]
            if "otqulo" in page_url:
                continue
            location_request = session.get(page_url)
            location_soup = BeautifulSoup(location_request.text, "lxml")
            if (
                "OPENING IN" in location_soup.text.upper()
                or "now closed and relocating" in location_soup.text.lower()
                or "PERMANENTLY CLOSED" in location_soup.text.upper()
            ):
                continue
            try:
                iframe = location_soup.find("iframe")["src"]
            except:
                continue
            geo_request = session.get(iframe, headers=headers)
            geo_soup = BeautifulSoup(geo_request.text, "lxml")
            script = geo_soup.find_all("script", text=re.compile("initEmbed"))[
                0
            ].contents[0]
            street_address = (
                list(
                    location_soup.find(
                        "font", {"face": "arial, helvetica"}
                    ).stripped_strings
                )[0]
                .split("(")[0]
                .split(" at ")[0]
                .split(" Tel:")[0]
                .strip()
            )
            if "initEmbed" in script:
                try:
                    geo_data = json.loads(script.split("initEmbed(")[1].split(");")[0])[
                        21
                    ][3][0][1]
                    lat = json.loads(script.split("initEmbed(")[1].split(");")[0])[21][
                        3
                    ][0][2][0]
                    lng = json.loads(script.split("initEmbed(")[1].split(");")[0])[21][
                        3
                    ][0][2][1]
                except:
                    geo_data = "<MISSING>"
                    lat = "<MISSING>"
                    lng = "<MISSING>"
            if geo_data == "<MISSING>":
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
            else:
                if (
                    "Shopping Center" in street_address
                    or not street_address[0].isdigit()
                    or "Mall" in street_address
                    or len(street_address) < 15
                ):
                    street_address = " ".join(geo_data.split(",")[0:-2]).strip()
                city = geo_data.split(",")[-2].strip()
                state = geo_data.split(",")[-1].split(" ")[1].strip()
                zipp = geo_data.split(",")[-1].split(" ")[-1].strip()
            street_address = (
                street_address.replace("Stoneridge Mall Rd", "1 Stoneridge Mall Rd")
                .replace("  ", " ")
                .replace(", Oakland, CA", "")
                .replace("University of California Davis", "")
            ).strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]
            if "Hwy 280 & Serramonte Blvd" in location_soup.text:
                street_address = "Hwy 280 & Serramonte Blvd."
            store = []
            store.append("http://quicklyusa.com")
            store.append(location.text)
            store.append(street_address if street_address != "" else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(page_url)

            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
