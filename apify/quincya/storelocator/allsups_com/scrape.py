from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://allsups.com/wp-content/themes/allsups/locations/locations.json"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://allsups.com"

    for i in stores:
        store_number = i["id"]
        store = i["acf"]
        location_name = (
            store["business_name"] + " Store #" + store["internal_store_code"][-4:]
        )
        if "allsup" not in location_name.lower():
            continue
        street_address = (
            store["address_line_1"] + " " + store["address_line_2"]
        ).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = store["country"]
        phone = store["primary_phone"]
        location_type = ""
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = (
            "Sunday: "
            + store["sunday"]
            + " Monday: "
            + store["monday"]
            + " Tuesday: "
            + store["tuesday"]
            + " Wednesday: "
            + store["wednesday"]
            + " Thursday: "
            + store["thursday"]
            + " Friday: "
            + store["friday"]
            + " Saturday: "
            + store["saturday"]
        )
        link = "https://allsups.com/find-location/?id=" + str(store_number)
        if "00" not in hours_of_operation:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = " ".join(
                list(base.find(class_="list-unstyled").stripped_strings)
            )
        if "Sunday: Monday: Tuesday:" in hours_of_operation:
            hours_of_operation = ""

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
