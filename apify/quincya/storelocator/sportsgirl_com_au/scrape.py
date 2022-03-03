import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.sportsgirl.com.au/storelocator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base_str = str(BeautifulSoup(req.text, "lxml"))

    locator_domain = "https://www.sportsgirl.com.au"

    js = base_str.split('defaultLocations":')[1].split("}}}")[0] + "}}}"
    items = json.loads(js)["store"]["items"]

    for item in items:

        link = item["url_key"]
        location_name = item["name"]
        raw_address = item["street"]
        if raw_address[-1:] == ",":
            raw_address = raw_address[:-1]
        if "," in raw_address:
            street_address = raw_address.split(",")[-1].strip()
        else:
            street_address = raw_address

        if "Building" in street_address or "214 Rockhampton" in street_address:
            street_address = raw_address.split(",")[-2].strip()

        if "Shop" in street_address:
            street_address = " ".join(street_address.split()[2:]).strip()

        city = item["city"]
        state = item["state"]
        zip_code = item["postcode"]
        country_code = item["country"]
        store_number = item["entity_id"]
        location_type = ""
        phone = item["phone_number"]
        latitude = item["latitude"]
        longitude = item["longitude"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = " ".join(
            list(base.find(class_="content hours").table.stripped_strings)
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
