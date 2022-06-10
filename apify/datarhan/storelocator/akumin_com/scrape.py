import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    domain = "akumin.com"
    start_url = "https://akumin.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[contains(@class, "location")]/a/@href')

    for store_url in all_locations:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = (
            loc_dom.xpath('//div[@class="breadcrumb"]/text()')[-1]
            .replace("/", "")
            .strip()
        )
        poi = loc_dom.xpath('//script[@class="yext-schema-json"]/text()')
        raw_adr = loc_dom.xpath('//div[strong[contains(text(), "Address:")]]/text()')
        raw_adr = [e.strip() for e in raw_adr if e.strip()]
        street_address = raw_adr[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if poi:
            poi = json.loads(poi[0])
            hoo = []
            for e in poi["openingHoursSpecification"]:
                if not e.get("dayOfWeek"):
                    continue
                if e.get("opens"):
                    hoo.append(f'{e["dayOfWeek"]} {e["opens"]} - {e["closes"]}')
                else:
                    hoo.append(f'{e["dayOfWeek"]} closed')
            hoo = " ".join(hoo)
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            store_number = poi["@id"]
            phone = poi["telephone"]
            loc_type = ", ".join(poi["@type"])
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            city = raw_adr[1].split(", ")[0]
            state = raw_adr[1].split(", ")[-1].split()[0]
            zip_code = raw_adr[1].split(", ")[-1].split()[-1]
            store_number = SgRecord.MISSING
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
            loc_type = SgRecord.MISSING
            geo = re.findall(
                r"google.maps.LatLng\((.+?)\);", str(etree.tostring(loc_dom))
            )[0].split(", ")
            latitude = geo[0]
            longitude = geo[1]
        if len(state) > 2:
            state = ""
        temp_closed = loc_dom.xpath('//strong[@class="center_temp_closed"]')
        if temp_closed:
            hoo = "Temporarily Closed"

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
            phone=phone,
            location_type=loc_type,
            latitude=latitude,
            longitude=longitude,
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
