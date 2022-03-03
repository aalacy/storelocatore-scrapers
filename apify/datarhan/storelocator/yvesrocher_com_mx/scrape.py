from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://uberall.com/api/storefinders/2uSpo3QpFD9gt72dwdcrXoHGavm7NY/locations/all?v=20211005&language=es&="
    domain = "yvesrocher.com.mx"
    hdr = {
        "Host": "uberall.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations["response"]["locations"]:
        street_address = poi["streetAndNumber"]
        if poi["addressExtra"]:
            street_address += ", " + poi["addressExtra"]
        page_url = f'https://www.yvesrocher.com.mx/ComoComprar/StoreLocator#!/l/{poi["city"].lower()}/{poi["streetAndNumber"].lower().replace(" ", "-")}/{poi["id"]}'
        days = {
            1: "mar.",
            2: "mié.",
            3: "jue.",
            4: "vie.",
            5: "sáb.",
            6: "dom.",
            7: "lun.",
        }
        hoo = []
        for e in poi["openingHours"]:
            hoo.append(f'{days[e["dayOfWeek"]]} {e["from1"]} - {e["to1"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address.strip(),
            city=poi["city"],
            state=poi["province"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["identifier"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
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
