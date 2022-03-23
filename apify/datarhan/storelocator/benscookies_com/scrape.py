from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.benscookies.com/wp-admin/admin-ajax.php"
    domain = "benscookies.com"
    hdr = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    all_locations = session.post(
        start_url, headers=hdr, data={"action": "store_list"}
    ).json()
    for poi in all_locations:
        raw_adr = f'{poi["address"]["street"]} {poi["address"]["towncity"]} {poi["address"]["postcodezip_code"]}'
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = []
        for day, hours in poi["openingtimes"].items():
            if day == "bankhols":
                continue
            hoo.append(f"{day} {hours}")
        hoo = " ".join(hoo)
        latitude = ""
        longitude = ""
        if poi["coordinates"]:
            latitude = poi["coordinates"]["latitude"]
            longitude = poi["coordinates"]["longitude"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.benscookies.com/our-stores/",
            location_name=poi["title"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=poi["address"]["tel"],
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
