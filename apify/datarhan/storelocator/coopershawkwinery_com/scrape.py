import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "chwinery.com"

    start_url = "https://chwinery.com/locations?near=50210&distance=10000-miles"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Location Details")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="location-info__heading"]/text()')
        if location_name:
            location_name = location_name[0] if location_name else ""
            raw_address = loc_dom.xpath(
                '//div[@class="location-info__details"]/div/p[1]/text()'
            )[:2]
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            street_address = ""
            if len(raw_address) == 2:
                street_address = raw_address[0]
            street_address = street_address.strip() if street_address else ""
            city = raw_address[-1].split(", ")[0].strip()
            state = raw_address[-1].split(", ")[-1].split()[0]
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            phone = loc_dom.xpath(
                '//h2[contains(text(),"Contact")]/following-sibling::p/text()'
            )
            phone = phone[-1].split(":")[-1] if phone else ""
            is_tc = loc_dom.xpath('//span[contains(@class, "callout-label")]/text()')
            if is_tc:
                if is_tc[0] == "Coming Soon":
                    continue
            geo = loc_dom.xpath("//div/@data-dna")[0]
            geo = json.loads(geo)
            latitude = geo[0]["locations"][0]["lat"]
            latitude = latitude if latitude else ""
            longitude = geo[0]["locations"][0]["lng"]
            longitude = longitude if longitude else ""
            hours_of_operation = loc_dom.xpath('//table[@class="hours-table"]//text()')
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )
        else:
            poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
            poi = json.loads(poi)
            poi = poi["@graph"][1]
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            phone = poi["telephone"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = []
            for e in poi["openingHoursSpecification"]:
                day = e["dayOfWeek"][0]
                opens = e["opens"][:-3]
                closes = e["closes"][:-3]
                hoo.append(f"{day}: {opens} - {closes}")
            hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
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
