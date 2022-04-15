from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.muvfitness.com/wp-admin/admin-ajax.php?action=store_search&lat=45.336447&lng=-122.605042&max_results=100&search_radius=500&autoload=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.muvfitness.com"

    for store in stores:
        street_address = store["address"].replace("\ufeff", "").strip()
        city = store["city"]
        state = store["state"].replace("Washington", "WA").strip()
        zip_code = store["zip"]
        country_code = "US"
        location_type = "<MISSING>"
        store_number = store["id"]
        phone = store["phone"].replace("\ufeff", "").strip()
        link = locator_domain + store["url"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h2.text
        try:
            hours_of_operation = " ".join(
                list(base.find(class_="tag_hours_table").stripped_strings)
            ).strip()
            if "mon" not in hours_of_operation.lower():
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = ""

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
