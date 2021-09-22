from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://webapi.burgerking.fr/blossom/api/v12/public/store-locator"
    domain = "burgerking.fr"

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "undefined",
        "x-platform": "WEB",
        "x-application": "WEBSITE",
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["markers"]
    for poi in all_locations:
        url = f'https://webapi.burgerking.fr/blossom/api/v12/public/restaurant/{poi["id"]}'
        poi = session.get(url, headers=hdr).json()
        hoo = ""
        if poi.get("openingHour"):
            hoo = f'{poi["openingHour"]} - {poi["closingHour"]}'

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.burgerking.fr/restaurants",
            location_name=poi["name"],
            street_address=poi["addressFull"].split(" - ")[0],
            city=" ".join(poi["addressFull"].split(" - ")[-1].split()[1:]),
            state=SgRecord.MISSING,
            zip_postal=poi["addressFull"].split(" - ")[-1].split()[0],
            country_code="FR",
            store_number=poi["id"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
