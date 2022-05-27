import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://jiffytrip.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "storenum" in str(script):
            script = str(script)
            break
    js = script.split('"places":')[1].split(',"listing')[0]
    stores = json.loads(js)

    locator_domain = "https://jiffytrip.com/"

    for store in stores:
        location_name = store["title"]
        street_address = store["address"].split(",")[0]
        city = store["location"]["city"]
        state = store["location"]["state"]
        zip_code = store["location"]["postal_code"]
        country_code = "US"
        store_number = store["location"]["extra_fields"]["storenum"]
        phone = store["location"]["extra_fields"]["phone"]
        location_type = store["location"]["extra_fields"]["fuels"]
        if location_type[-1:] == ",":
            location_type = location_type[:-1]
        latitude = store["location"]["lat"]
        longitude = store["location"]["lng"]
        hours_of_operation = store["location"]["extra_fields"]["hours"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
