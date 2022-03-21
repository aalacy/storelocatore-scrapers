from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    categories = {
        "1": "Sales, Service, Spareparts",
        "3": "Sales",
        "6": "Sales, Service Point",
    }
    for cat, location_type in categories.items():
        start_url = f"https://www.suzuki.co.id/dealers/search?keyword=&category={cat}&province=&type=automobile"
        domain = "suzuki.co.id"
        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
        }
        data = session.get(start_url, headers=hdr).json()
        for poi in data["dealers"]:
            raw_address = " ".join(poi["address"].split())
            city = poi["city"]
            addr = parse_address_intl(raw_address)
            street_address = ", ".join(raw_address.split(city)[0].split(", ")[:-1])
            phone = (
                poi["phone"]
                .split(";")[0]
                .split("/")[0]
                .split(",")[0]
                .split(".")[0]
                .split("(Hunting)")[0]
                .split("Hunting")[0]
                .strip()
            )
            if phone == "-":
                phone = ""

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.suzuki.co.id/dealers?t=automobile",
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="ID",
                store_number=poi["id"],
                phone=phone,
                location_type=location_type,
                latitude=poi["geo_lat"],
                longitude=poi["geo_lng"],
                hours_of_operation="",
                raw_address=raw_address,
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
