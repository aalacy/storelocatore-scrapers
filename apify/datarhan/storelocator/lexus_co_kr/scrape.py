from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.co.kr/data/json/getData_find_dealers.php?dealer=official&page_id=find_dealers"
    domain = "lexus.co.kr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for e in data["find_dealers"]["locations"]:
        for poi in e["branches"]:

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.lexus.co.kr/find-dealers/",
                location_name=poi["text"],
                street_address=poi["addr"],
                city="",
                state="",
                zip_postal="",
                country_code="KR",
                store_number="",
                phone=poi["tel"],
                location_type="",
                latitude=poi["map"]["latitude"],
                longitude=poi["map"]["longitude"],
                hours_of_operation="",
                raw_address=poi["addr"],
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
