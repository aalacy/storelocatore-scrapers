import json
import os

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-gb:{}@proxy.apify.com:8000/"


def fetch_data(sgw: SgWriter):
    base_link = "https://www.odeoncinemas.ie/cinemas/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.odeoncinemas.ie"

    items = json.loads(base.find(id="v-site-list-all-cinemas")["data-v-site-list"])[
        "config"
    ]["cinemas"]

    for item in items:

        link = "https://www.odeoncinemas.ie" + item["url"]
        location_name = item["name"]
        raw_address = (
            item["addressLine1"].strip()
            + " "
            + item["addressLine2"].strip()
            + " "
            + item["addressLine3"].strip()
            + " "
            + item["addressLine4"].strip()
            + " "
            + item["postCode"].strip()
        ).strip()
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        if not city:
            city = item["addressLine4"]
        if not city:
            city = item["addressLine2"]
        if not city or city in street_address:
            city = location_name
        state = addr.state
        zip_code = addr.postcode
        state = "<MISSING>"
        country_code = "Ireland"
        store_number = item["id"]
        if item["isImax"]:
            location_type = "IMAX"
        else:
            location_type = "Cinema"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = item["latitude"]
        longitude = item["longitude"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address.replace("'S", "'s"),
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
