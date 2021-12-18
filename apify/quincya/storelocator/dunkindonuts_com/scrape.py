from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.dunkindonuts.com/bin/servlet/dsl?service=DSL&origin=24.676506%2C-81.3179364&radius=5000&maxMatches=10000&pageSize=1&units=m&ambiguities=ignore"

    session = SgRequests()
    stores = session.post(base_link).json()["data"]["storeAttributes"]

    locator_domain = "https://www.dunkindonuts.com"

    found = []
    for store in stores:
        location_name = store["name"]
        if "DO NOT USE" in store["address2"].upper():
            continue
        street_address = store["address"]
        if (
            "suit" in store["address2"].lower()
            or "unit" in store["address2"].lower()
            or "blvd" in store["address2"].lower()
            or "ste" in store["address2"].lower()
            or " rd" in store["address2"].lower()
            or " dr" in store["address2"].lower()
        ):
            street_address = street_address + " " + store["address2"]

        city = store["city"]

        if street_address + city in found:
            continue
        found.append(street_address + city)

        state = store["state"]
        zip_code = store["postal"]
        country_code = store["country"]
        store_number = store["recordId"]
        location_type = ""
        phone = store["phonenumber"].replace("813-443-232", "813-443-0232")
        if "--" in phone:
            phone = "<INACCESSIBLE>"
        hours_of_operation = (
            "Mon "
            + store["mon_hours"].replace(" ", "Closed")
            + " Tue "
            + store["tue_hours"].replace(" ", "Closed")
            + " Wed "
            + store["wed_hours"].replace(" ", "Closed")
            + " Thu "
            + store["thu_hours"].replace(" ", "Closed")
            + " Fri "
            + store["fri_hours"].replace(" ", "Closed")
            + " Sat "
            + store["sat_hours"].replace(" ", "Closed")
            + " Sun "
            + store["sun_hours"].replace(" ", "Closed")
        )
        latitude = store["lat"]
        longitude = store["lng"]

        link = "https://locations.dunkindonuts.com/en/" + store_number

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
