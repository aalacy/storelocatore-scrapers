from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://burgerking.com.br/api/nearest"
    domain = "burgerking.com.br"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json;charset=utf-8",
    }
    frm = {"address": "rio", "localization": {}}
    data = session.post(start_url, headers=hdr, json=frm).json()

    for poi in data["entries"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://burgerking.com.br/restaurantes",
            location_name=poi["title"],
            street_address=poi["addressLineOne"],
            city=poi["locality"],
            state=poi["administrativeArea"],
            zip_postal=SgRecord.MISSING,
            country_code="BR",
            store_number=poi["storeCode"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=SgRecord.MISSING,
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
