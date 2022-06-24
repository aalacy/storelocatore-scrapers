import json
import time

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "winsupplyinc.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=200,
        expected_search_radius_miles=None,
    )

    post_url = "https://www.winsupplyinc.com/rest/model/com/ws/supplier/SupplierActor/searchAdditionalSupplier?{}"
    body = '{"location":"10001","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":""}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.post(
        post_url.format(str(int(time.time() * 1000))), headers=headers, data=body
    )

    body = '{"location":"10001","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":"%s"}'
    response = session.get(
        "https://www.winsupplyinc.com/rest/model/atg/rest/SessionConfirmationActor/getSessionConfirmationNumber",
        headers=headers,
    )
    session_data = json.loads(response.text)
    session_no = session_data["sessionConfNo"]
    headers["Content-Type"] = "application/json"

    for code in all_codes:
        body = '{"location":"%s","distance":"250","industryType":"","showroomOnly":false,"_dynSessConf":"%s"}'
        response = session.post(
            post_url.format(str(int(time.time() * 1000))),
            headers=headers,
            data=body % (code, session_no),
        )
        data = json.loads(response.text)

        if not data.get("additionalSupplier"):
            continue

        for poi in data["additionalSupplier"]:
            page_url = "https://www.winsupplyinc.com" + poi["seoURL"]
            location_name = poi["displayName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            if poi["address3"]:
                street_address += ", " + poi["address3"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["postalCode"]
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hours_of_operation = " ".join(poi["timings"])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
