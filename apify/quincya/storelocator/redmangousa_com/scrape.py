from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=TXEJGBXGVEQUABKM&country=US&multi_account=false"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["locations"]

    locator_domain = "redmangousa.com"

    for i in stores:
        location_name = "Red Mango"
        street_address = i["store_info"]["address"].strip().replace(" ", "+")
        city = i["store_info"]["locality"].replace(" ", "+")
        state = i["store_info"]["region"].replace(" ", "+")

        api_link = (
            "https://api.momentfeed.com/v1/analytics/api/llp.json?address=%s&locality=%s&multi_account=false&pageSize=30&region=%s&auth_token=TXEJGBXGVEQUABKM"
            % (street_address, city, state)
        )
        store = session.get(api_link, headers=headers).json()[0]
        store = store["store_info"]
        location_name = store["name"]
        if "Permanently Closed" in location_name:
            continue
        street_address = store["address"].strip()
        city = store["locality"]
        state = store["region"]
        if not state:
            continue
        zip_code = store["postcode"]
        country_code = store["country"]
        store_number = store["corporate_id"]
        location_type = store["status"]
        phone = store["phone"]
        hours_of_operation = (
            store["store_hours"]
            .replace("0,", "0-")
            .replace("1,", "Mon ")
            .replace("2,", "Tue ")
            .replace("3,", "Wed ")
            .replace("4,", "Thu ")
            .replace("5,", "Fri ")
            .replace("6,", "Sat ")
            .replace("7,", "Sun ")
        )[:-1]
        if "Mon" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Mon Closed"
        if "Sat" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Sat Closed"
        if "Sun" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Sun Closed"
        if not hours_of_operation or "close" in location_type:
            hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = store["website"]

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
