import json

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    locator_domain = "https://www.riddlesjewelry.com/"

    session = SgRequests()

    for i in range(20):

        r = session.get(
            "https://www.riddlesjewelry.com/storelocator/index/ajax/?address_1=&address_2=&city=&region=&country_id=&zipcode=&current_page="
            + str(i),
            headers=headers,
        )

        k = r.json()
        for idx, val in enumerate(k["data"]):
            street_address = val["address"][0].strip()
            phone = val["telephone"]
            latitude = val["latitude"]
            longitude = val["longitude"]
            zip_code = val["zipcode"]
            state = val["region"]
            city = val["city"]
            location_name = val["storename"].replace("&#039;", "'")
            country_code = "US"
            store_number = val["storelocator_id"]
            page_url = locator_domain + val["url_key"]
            location_type = ""

            hours_of_operation = ""
            store_time = json.loads(val["storetime"])
            for row in store_time:
                if row["day_status"] == "1":
                    hours = (
                        row["days"]
                        + " "
                        + row["open_hour"]
                        + ":"
                        + row["open_minute"]
                        + "-"
                        + row["close_hour"]
                        + ":"
                        + row["close_minute"]
                    )
                else:
                    hours = row["days"] + " Closed"
                hours_of_operation = (hours_of_operation + " " + hours).strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
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
