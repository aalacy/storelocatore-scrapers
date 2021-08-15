import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "unode50.com"
    start_url = "https://www.unode50.com/us/stores#34.09510173134606,-118.3993182825743"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "calendar")]/text()')[0]
    data = json.loads(data)

    for poi in data["*"]["Magento_Ui/js/core/app"]["components"][
        "store-locator-search"
    ]["markers"]:
        location_name = poi["name"]
        if location_name == "g":
            continue
        if "., .," in poi["address"]:
            continue
        raw_address = poi["address"].replace("\n", ", ").replace("\t", ", ").split(", ")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        city = addr.city
        if not city:
            city = raw_address[-2]
        if city == "-":
            city = SgRecord.MISSING
        street_check = " ".join([e.capitalize() for e in poi["address"].split()]).split(
            city
        )
        if len(street_check) == 2:
            street_address = (
                " ".join([e.capitalize() for e in poi["address"].split()])
                .split(city)[0]
                .strip()
            )
        else:
            street_address = " ".join([e.capitalize() for e in raw_address[0].split()])
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if street_address == "South Market":
            street_address = "South Market, Bay 34"
        if street_address.isdigit():
            street_address = ", ".join(raw_address[:2])
        if street_address in ["-", "."]:
            street_address = SgRecord.MISSING
        street_address = street_address.replace(">> ", "").strip()
        if street_address == "12":
            street_address = ", ".join(raw_address[:2])
        state = addr.state
        zip_code = addr.postcode
        store_number = poi["id"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        store_url = f"https://www.unode50.com/en/int/stores#{latitude},{longitude}"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=poi["address"].replace("\n", ", ").replace("\t", ", "),
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
