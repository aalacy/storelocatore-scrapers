from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.com.mx/api/v1/dealerships?limit=72&sort=state ASC"
    domain = "suzuki.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(start_url, headers=hdr).json()
    for e in data["items"]:
        for poi in e["items"]:
            street_address = poi["street"]
            if street_address and poi["extNumber"]:
                street_address += " " + poi["extNumber"]
            else:
                street_address = poi["extNumber"]
            if poi["intNumber"]:
                street_address += " " + poi["intNumber"]
            if street_address and poi["suburb"]:
                street_address += ", " + poi["suburb"]
            if street_address == "1313":
                street_address = poi["address"].split(poi["suburb"])[0].strip()
            if not street_address:
                street_address = (
                    " ".join(poi["address"].split())
                    .split(poi["municipality"].strip())[0]
                    .strip()
                )
            if street_address.endswith(","):
                street_address = street_address[:-1]

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.suzuki.com.mx/autos/concesionarias",
                location_name=poi["name"],
                street_address=street_address,
                city=poi["municipality"],
                state=poi["state"],
                zip_postal=poi["zipCode"],
                country_code="MX",
                store_number=poi["id"],
                phone=poi["phone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation="",
                raw_address=" ".join(poi["address"].split()),
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
