import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.swamiscafe.com/our-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "swamiscafe.com"

    raw_data = base.find(id="popmenu-apollo-state").contents[0]
    js = raw_data.split("STATE =")[1].strip()[:-1]
    store_data = json.loads(js)

    for loc in store_data:
        if "RestaurantLocation:" in loc:
            store = store_data[loc]

            location_name = store["name"]
            street_address = store["streetAddress"]
            city = store["city"]
            state = store["state"]
            zip_code = store["postalCode"]
            country_code = "US"
            location_type = "<MISSING>"
            phone = store["displayPhone"]
            hours_of_operation = " ".join(store["schemaHours"])
            link = "https://www.swamiscafe.com/" + store["slug"]
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
