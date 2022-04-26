import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    base_link = "https://bills-website.co.uk/locations/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="nearest-bill-restorent-result").find_all(
        "a", string="View restaurant"
    )

    locator_domain = "https://bills-website.co.uk/"

    for item in items:
        link = item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = (
            base.find("script", attrs={"type": "application/ld+json"})
            .contents[0]
            .replace("\r\n", "")
        )
        store = json.loads(script)

        location_name = store["name"]

        address = store["address"]
        raw_address = address.split("Restaurant, ")[1]
        addr = parse_address_intl(raw_address)

        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode

        if not zip_code or len(zip_code) < 4:
            zip_code = raw_address.split(",")[-1]

        if zip_code.lower() in street_address.lower():
            street_address = " ".join(street_address.split(" ")[:-2])

        street_address = (
            street_address.replace("Rg12", "").replace("W6", "").replace("W12", "")
        )

        if not city:
            if "london" in location_name.lower():
                city = "London"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "UK"
        phone = store["telephone"]
        location_type = ""

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        hours_of_operation = " ".join(
            list(
                base.find(class_="banner-bottom-section")
                .find(class_="bottom-sec")
                .stripped_strings
            )[1:]
        )

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
