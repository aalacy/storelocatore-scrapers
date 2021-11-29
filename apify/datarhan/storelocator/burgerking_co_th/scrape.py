import json

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://apibgk.buzzebees.com/api/place?center=13.7451765,100.5081332&device_locale=1054&distance=1500000&mode=nearby&within_area=0&require_campaign=0&agencyId=7331&device_app_id=1351788021633457"
    domain = "burgerking.co.th"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        addr = parse_address_intl(poi["address_en"])
        street_address = poi["address_en"].split(", ")[0]
        phone = ""
        if poi["contact_number"]:
            phone_data = json.loads(poi["contact_number"])
            phone = phone_data.get("mobile_number")
            if not phone:
                phone = phone_data.get("contact_number")
        phone = phone if phone else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url="https://burgerking.co.th/locationbk",
            location_name=poi["name_en"],
            street_address=street_address,
            city=addr.city,
            state=poi["region"],
            zip_postal=addr.postcode,
            country_code=SgRecord.MISSING,
            store_number=poi["id"],
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=poi["location"]["latitude"],
            longitude=poi["location"]["longitude"],
            hours_of_operation=poi["working_day_en"],
            raw_address=poi["address_en"],
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
