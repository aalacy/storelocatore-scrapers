from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.grahamdirect.co.uk/wp-admin/admin-ajax.php?action=store_search&lat=55.378051&lng=-3.435973&max_results=100&search_radius=500"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "grahamdirect.co.uk"

    for store in stores:
        try:
            street_address = (
                store["address"].strip() + " " + store["address2"].strip()
            ).strip()
        except:
            street_address = store["address"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        location_name = store["store"].replace("&#8211;", "-").replace("&#8217;", "")
        country_code = store["country"]

        if city in street_address[-30:]:
            street_address = street_address[: street_address.rfind(city)].strip()

        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://www.grahamdirect.co.uk/branch-locator/"
        hours_of_operation = " ".join(
            BeautifulSoup(store["hours"], "lxml").stripped_strings
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
