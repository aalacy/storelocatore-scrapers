from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://parisbaguette.com/wp-admin/admin-ajax.php?action=store_search&lat=40.51296&lng=-74.40854&max_results=500&search_radius=50&autoload=1"

    session = SgRequests(verify_ssl=False)
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://parisbaguette.com"

    for store in stores:
        location_name = store["store"].replace("#038;", "").replace("&#8211;", "-")
        street_address = (store["address"] + " " + store["address2"]).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        try:
            hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
            if not hours_of_operation:
                hours_of_operation = " ".join(
                    list(
                        BeautifulSoup(
                            store["markup"]["store_hours"], "lxml"
                        ).stripped_strings
                    )
                ).title()
        except:
            hours_of_operation = " ".join(
                list(
                    BeautifulSoup(
                        store["markup"]["store_hours"], "lxml"
                    ).stripped_strings
                )
            ).title()
        hours_of_operation = hours_of_operation.replace(
            "Mon Tue Wed Thu Fri Sat Sun", ""
        )
        latitude = store["lat"]
        longitude = store["lng"]
        if store["markup"]["coming_soon"]:
            continue

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://parisbaguette.com/locations/",
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
