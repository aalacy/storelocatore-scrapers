import re
import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_url = "https://www.theeyedoctors.net/"

    link_soup = BeautifulSoup(
        session.get("https://www.theeyedoctors.net/locations").text, "lxml"
    )

    all_scripts = link_soup.find_all("script")
    for script in all_scripts:
        if "address1" in str(script):
            script = str(script)
            break

    js = script.split('locations":')[1].split(',"currentSlug')[0]
    stores = json.loads(js)

    for store in stores:
        page_url = "https://www.theeyedoctors.net/locations/" + store["slug"]

        location_soup = BeautifulSoup(session.get(page_url).text, "lxml")
        location_name = location_soup.h1.text.strip()
        addr = list(location_soup.address.stripped_strings)

        street_address = " ".join(addr[:-1]).replace(",", "").split("Topeka")[0].strip()

        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[1].split()[0].strip()
        zipp = addr[-1].split(",")[1].split()[1].strip()

        phone = location_soup.address.find_next("a").text.strip()

        store_number = ""
        location_type = ""

        latitude = (
            re.findall(r'latitude": "[0-9]{2}\.[0-9]+', str(location_soup))[0]
            .split(":")[1][1:]
            .replace('"', "")
        )
        longitude = (
            re.findall(r'longitude": "-[0-9]{2,3}\.[0-9]+', str(location_soup))[0]
            .split(":")[1][1:]
            .replace('"', "")
        )

        hours = (
            " ".join(
                list(
                    location_soup.find(
                        "div", {"class": "w-full md:w-2/3 mt-4"}
                    ).stripped_strings
                )
            )
            .split("This")[0]
            .strip()
        )

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
