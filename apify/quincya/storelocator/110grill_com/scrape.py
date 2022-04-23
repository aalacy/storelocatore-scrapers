import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.110grill.com/locations"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "upgrade-insecure-requests": "1",
    }

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    raw_data = base.find(id="popmenu-apollo-state").contents[0]
    js = raw_data.split("STATE =")[1].strip()[:-1].replace('scr" + "ipt', "script")
    store_data = json.loads(js)

    locator_domain = "https://www.110grill.com/"

    for loc in store_data:
        if "RestaurantLocation:" in loc:
            store = store_data[loc]
            location_name = store["name"]
            street_address = store["streetAddress"]
            city = store["city"]
            state = store["state"]
            zip_code = store["postalCode"]
            country_code = "US"
            phone = store["displayPhone"]
            location_type = "<MISSING>"
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]
            link = locator_domain + store["slug"]
            hours_of_operation = " ".join(store["schemaHours"])
            days = ["Su ", "Mo ", "Tu ", "We ", "Th ", "Fr ", "Sa "]
            for day in days:
                if day not in hours_of_operation:
                    hours_of_operation = hours_of_operation + " " + day + "Closed"
            hours_of_operation = hours_of_operation.strip()

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
