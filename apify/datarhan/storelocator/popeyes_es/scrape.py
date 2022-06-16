from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="es")
    start_url = "https://api.airtouchpop.com/api/v1/restaurants?language=null&key=3RtSwmF8KAelm98PaNJJYrRpP7iGONJJuOIlXef9w29Psb3Ue6Lzquu9TrKY39i6"
    domain = "popeyes.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations["data"]:
        hoo = []
        for day, hours in poi["schedule"].items():
            hoo.append(f"{day} {hours}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.popeyes.es/restaurantes",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state="",
            zip_postal=poi["postalCode"],
            country_code="ES",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
