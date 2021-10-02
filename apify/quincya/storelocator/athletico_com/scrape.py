import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.athletico.com/search-locations/?address=85282&lat=&lng=&service=&insurance=&language=&submitted=submitted"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = str(base).split("json = ")[1].split("};")[0] + "}"
    stores = json.loads(js)["locations"]

    locator_domain = "athletico.com"

    for store in stores:
        location_name = store["post_title"]
        if "coming soon" in location_name.lower():
            continue

        street_address = (store["address"] + " " + store["address_line_2"]).strip()
        city = store["city"].strip()
        state = store["state"]
        zip_code = store["zip"]

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]
        else:
            if "," in city:
                street_address = city.split(",")[0].strip()
                city = city.split(",")[1].strip()

        if not city:
            city = street_address.split(",")[1].strip()
            street_address = street_address.split(",")[0].strip()

        country_code = "US"
        store_number = store["id"]
        location_type = ""
        phone = store["phone"]
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        hours_of_operation = " ".join(
            list(BeautifulSoup(store["hours"], "lxml").stripped_strings)
        )
        link = "https://www.athletico.com/locations/" + store["post_name"]

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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
