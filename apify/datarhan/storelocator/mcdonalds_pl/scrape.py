from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://mcdonalds.pl/data/places"
    domain = "mcdonalds.pl"
    data = session.get(start_url).json()

    all_locations = data["places"]
    for poi in all_locations:
        hoo = []
        days_dict = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday",
        }
        for d, h in poi["hours"].items():
            day = days_dict[d]
            hoo.append(f'{day} {h["from"]} - {h["to"]}')
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=f'https://mcdonalds.pl/restauracje/{poi["slug"]}',
            location_name=SgRecord.MISSING,
            street_address=poi["address"],
            city=poi["city"],
            state=poi["province"],
            zip_postal=poi["postCode"],
            country_code="PL",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
