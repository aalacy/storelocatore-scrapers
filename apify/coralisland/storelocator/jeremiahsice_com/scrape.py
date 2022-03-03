from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://jeremiahsice.com/locationlist"
    domain = "jeremiahsice.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for i, poi in all_locations.items():
        if "duplicate" in poi["slug"]:
            continue
        if poi["coming_soon"] == "1":
            continue
        hoo = []
        for k, time in poi.items():
            if "summer" in k:
                continue
            if "hours" in k:
                hoo.append(f'{k.split("_")[0]} {time}')
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://jeremiahsice.com/locations/" + poi["slug"],
            location_name=poi["title"],
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=SgRecord.MISSING,
            store_number=poi["store_id"],
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
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
