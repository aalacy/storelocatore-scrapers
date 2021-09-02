from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://restauracie.mcdonalds.sk/api?token=7983978c4175e5a88b9a58e5b5c6d105217fbc625b6c20e9a8eef3b8acc6204f"
    domain = "mcdonalds.sk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["restaurants"]:
        days = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]
        hoo = []
        for i, day in enumerate(days):
            hoo.append(f'{day} {poi["worktime"][i]}')
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=urljoin("https://restauracie.mcdonalds.sk/", poi["slug"]),
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=SgRecord.MISSING,
            zip_postal=poi["zip"],
            country_code="SK",
            store_number=poi["id"],
            phone=poi["telephone"],
            location_type=SgRecord.MISSING,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
