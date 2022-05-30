import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.coit.com/locator"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//caption[contains(text(), "COIT Locations")]/following-sibling::tbody//td/a[@hreflang="en"]/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        if "coming-soon" in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["provider"]["name"]
            street_address = poi["provider"]["address"]["streetAddress"].strip()
            city = poi["provider"]["address"]["addressLocality"].strip()
            state = poi["provider"]["address"]["addressRegion"].strip()
            zip_code = poi["provider"]["address"]["postalCode"].strip()
            country_code = poi["provider"]["address"]["addressCountry"]
            store_number = "<MISSING>"
            phone = poi["provider"]["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["serviceType"]
            if poi["provider"].get("geo"):
                latitude = poi["provider"]["geo"]["latitude"]
                longitude = poi["provider"]["geo"]["longitude"]
            else:
                geo = (
                    loc_dom.xpath('//img[contains(@src, "markers")]/@src')[0]
                    .split("=")[-1]
                    .split(",")
                )
                latitude = geo[0]
                longitude = geo[1]
            hoo = []
            if poi["provider"].get("openingHoursSpecification"):
                for day in poi["provider"]["openingHoursSpecification"]["dayOfWeek"]:
                    opens = poi["provider"]["openingHoursSpecification"]["opens"]
                    closes = poi["provider"]["openingHoursSpecification"]["closes"]
                    hoo.append(f"{day} {opens} {closes}")
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        else:
            location_name = loc_dom.xpath('//div/h1[@class="text-center"]/text()')
            if not location_name:
                continue
            location_name = location_name[0]
            street_address = loc_dom.xpath('//span[@class="address-line1"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
            city = loc_dom.xpath('//span[@class="locality"]/text()')[0].strip()
            if city.endswith(","):
                city = city[:-1]
            if street_address == city:
                street_address = "<MISSING>"
            state = loc_dom.xpath('//span[@class="administrative-area"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')[0]
            country_code = loc_dom.xpath('//span[@class="country"]/text()')[0]
            store_number = "<MISSING>"
            phone = (
                loc_dom.xpath('//p[contains(text(), "Phone:")]/text()')[0]
                .split(":")[-1]
                .strip()
            )
            location_type = "<MISSING>"
            geo = (
                loc_dom.xpath('//img[contains(@src, "markers")]/@src')[0]
                .split("=")[-1]
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
