from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://reservations.fourseasons.com/content/en/regions"
    domain = "fourseasons.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for reg in data["regions"]:
        for e in reg["properties"]:
            api_url = urljoin(start_url, e["urlApi"])
            poi = session.get(api_url).json()
            page_url = "https://www.fourseasons.com/" + poi["urlName"]
            raw_address = f'{poi.get("street")} {poi.get("city")} {poi.get("state")} {poi.get("zipcode")}'.replace(
                "None", ""
            ).strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.replace("DUBAI", "").strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["shortName"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code=poi["enCountry"],
                store_number=poi["owsCode"],
                phone=poi["propertyPhone"],
                location_type=poi["typeName"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation="",
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
