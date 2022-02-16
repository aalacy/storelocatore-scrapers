import json
import urllib.parse

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("bulgari_com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.bulgari.com/en-us/storelocator/"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    found = []
    base_links = base.find(class_="cell store-continet-list").find_all("a")
    for i in base_links:
        base_link = i["href"]

        logger.info(base_link)
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "bulgari.com"

        js = base.find(class_="map-canvas")["data-locations"]
        stores = json.loads(js)

        for store in stores:

            location_name = store["name"]
            city = store["storeCity"].replace("+", " ").title()
            city = urllib.parse.unquote(city)

            country_code = (
                store["storeCountry"]
                .replace("+", " ")
                .replace("r%C3%A9union", "Réunion")
                .title()
            )
            country_code = urllib.parse.unquote(country_code)
            store_number = store["storeId"]
            location_type = store["itemSubtitle"]
            try:
                phone = store["storePhone"].strip()
            except:
                phone = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = (
                "https://www.bulgari.com/en-us/storelocator/"
                + store["storeCountry"]
                + "/"
                + store["storeCity"]
                + "/"
                + store["storeNameUrl"]
                + "-"
                + store_number
            )

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                raw_address = base.find(
                    class_="storelocator-bread-subtitle"
                ).a.text.strip()
            except:
                continue

            addr = parse_address_intl(raw_address)
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1

            state = addr.state
            try:
                zip_code = addr.postcode.replace("REGION", "").strip()
            except:
                zip_code = ""

            if street_address:
                for zp in ["Sw1X 7Xl", "277-0842"]:
                    if zp in street_address:
                        zip_code = zp
                        street_address = street_address.replace(zp, "").strip()

            if not street_address or len(street_address) < 10:
                street_address = "".join(
                    base.find(class_="storelocator-bread-subtitle")["streetaddress"]
                    .strip()
                    .split(",")[:-1]
                )
                if len(street_address) < 10:
                    street_address = base.find(class_="storelocator-bread-subtitle")[
                        "streetaddress"
                    ].strip()

                if city:
                    if city in street_address:
                        street_address = street_address[
                            : street_address.rfind(city)
                        ].strip()

            if country_code in ["United States", "Canada"]:
                n_raw_address = (
                    base.find(class_="storelocator-bread-subtitle")["streetaddress"]
                    .strip()
                    .split(",")
                )
                state = n_raw_address[-1].strip()
                if not state:
                    raw_state = (
                        base.find(class_="storelocator-bread-subtitle")
                        .text.replace("\n", " ")
                        .strip()
                    )
                    state = raw_state[
                        raw_state.rfind(",") + 1 : raw_state.rfind(" ")
                    ].strip()

            if state:
                if state == "Kong":
                    state = "Hong Kong"

            if zip_code:
                zip_code = (
                    zip_code.replace("DOME", "").replace("GOVERNORATE", "").strip()
                )

            if country_code == "United States":
                states = ["Tx", "Pa", "Ny", "Fl", "Ct", "Co", "Va"]
                for st in states:
                    if st.lower() in street_address.split()[-1].lower():
                        street_address = " ".join(street_address.split()[:-1])

            if country_code == "Canada":
                zip_code = state[-7:].strip()
                state = state[:-7].strip()

            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="store-hours clearfix").stripped_strings)
                )
                if (
                    hours_of_operation
                    == "monday - tuesday - wednesday - thursday - friday - saturday - sunday -"
                ):
                    hours_of_operation = ""
            except:
                hours_of_operation = "<MISSING>"

            street_address = street_address.replace("<Br<", "").strip()
            if location_name + street_address in found:
                continue
            found.append(location_name + street_address)

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
