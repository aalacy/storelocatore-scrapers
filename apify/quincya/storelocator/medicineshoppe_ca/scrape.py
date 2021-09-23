from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.medicineshoppe.ca/api/sitecore/Pharmacy/Pharmacies?id=%7B4E561A90-2FD9-4AAC-ACCA-8572A82032AB%7D"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["pharmacies"]

    locator_domain = "medicineshoppe.ca"

    for store in stores:
        location_name = store["title"]
        raw_address = store["address"].split(",")
        street_address = " ".join(raw_address[:-3])
        city = raw_address[-3].strip()
        state = raw_address[-2].replace("(", "").replace(")", "").strip()
        zip_code = raw_address[-1].strip()
        country_code = "CA"
        store_number = store["storeCode"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["location"]["latitude"]
        longitude = store["location"]["longitude"]
        link = "https://www.medicineshoppe.ca" + store["detailUrl"]
        if not phone:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            try:
                phone = list(
                    base.find(class_="pharmacy-info-rx-phone").stripped_strings
                )[-1]
            except:
                phone = ""

        hours_of_operation = ""
        raw_hours = store["storeOpeningHours"]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hour["day"]
                + " "
                + raw_hour["openDuration"]
            ).strip()

        if store["temporarilyClosed"]:
            hours_of_operation = "Temporarily Closed"

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
