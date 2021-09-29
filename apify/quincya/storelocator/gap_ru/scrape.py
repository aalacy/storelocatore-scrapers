from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://gap.ru/"

    session = SgRequests()

    city_ids = ["84", "85", "2203"]

    for city_id in city_ids:
        base_link = (
            "https://gap.ru/ajax/?controller=stock&action=getList&productCityId="
            + city_id
        )
        stores = session.post(base_link, headers=headers).json()["data"]["shops"]

        for store in stores:

            store_number = store["id"]
            location_name = "GAP"

            raw_address = store["address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            city = addr.city
            state = addr.state
            zip_code = addr.postcode

            country_code = "RU"
            location_type = store["name"]
            phone = store["phone"]
            latitude = store["coords"]["lat"]
            longitude = store["coords"]["lng"]
            hours_of_operation = store["workTime"]
            link = "https://gap.ru/help/shops/"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
