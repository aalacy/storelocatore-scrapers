import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "riverisland.com"
    start_url = "https://www.riverisland.com/river-island-stores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(@class, "store-result__title")]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        store_number = re.findall('storeId = "(.+)?";', loc_response.text)[0]
        poi = session.get(
            f"https://www.riverisland.com/api/stores/{store_number}"
        ).json()
        poi = poi["data"]

        location_name = poi["storeDisplayName"]
        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += ", " + poi["address"]["line2"]
        if poi["address"]["line3"]:
            street_address += ", " + poi["address"]["line3"]
        street_address = street_address if street_address else "<MISSING>"
        raw_adr = f'{street_address} {poi["address"]["city"]}'
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += " " + addr.street_address_2
        if not street_address and addr.street_address_2:
            street_address = addr.street_address_2
        state = poi["address"]["stateCode"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["countryCode"]
        phone = poi["telephone"]
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        longitude = poi["location"]["longitude"]
        hoo = []
        if poi.get("storeOpeningHoursHtml"):
            hoo = etree.HTML(poi["storeOpeningHoursHtml"]).xpath("//text()")
            hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            "Monday" + " ".join(hoo).split(" Monday")[-1] if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
