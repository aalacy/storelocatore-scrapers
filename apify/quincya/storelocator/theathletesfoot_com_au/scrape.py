import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    base_link = "https://www.theathletesfoot.com.au/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = str(BeautifulSoup(req.text, "lxml"))

    locator_domain = "https://www.theathletesfoot.com.au/"

    js = base.split('defaultLocations":')[1].split("}}}")[0] + "}}}"
    items = json.loads(js)["store"]["items"]

    for item in items:

        link = item["url_key"]
        location_name = item["name"]
        city = item["city"]
        raw_address = item["street"].replace("  ", ", ")
        if "," in raw_address:
            street_address = raw_address.split(",")[-1].strip()
        else:
            street_address = raw_address

        street_address = (
            street_address.replace("Shop 30 Kingaroy Shopping World", "")
            .replace("Shop 5/109", "")
            .replace("Batemans Bay Village", "")
            .strip()
        )

        if "Shopping" in street_address or street_address == city:
            street_address = raw_address.split(",")[-2].strip()

        state = item["state"]
        zip_code = item["postcode"]
        country_code = item["country"]
        store_number = item["entity_id"]
        location_type = ""
        phone = item["phone"]
        hours_of_operation = " ".join(
            list(BeautifulSoup(item["opening_hours"], "lxml").table.stripped_strings)
        )
        if "Regular hours" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Regular hours")[1].strip()
        if ". Monday" in hours_of_operation:
            hours_of_operation = (
                "Monday" + hours_of_operation.split(". Monday")[1].strip()
            )

        latitude = item["latitude"]
        longitude = item["longitude"]

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
