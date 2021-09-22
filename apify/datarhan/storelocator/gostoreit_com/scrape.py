import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.gostoreit.com/#"
    domain = "gostoreit.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//li/a[contains(@href, "/locations/")]/@href')
    for url in list(set(all_states)):
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "Available Units")]/@href')

    for page_url in list(set(all_locations)):
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            phone = poi["telephone"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = ""
            if poi.get("openingHours"):
                hoo = " ".join(poi["openingHours"])
        else:
            location_name = loc_dom.xpath("//h1/text()")[0]
            raw_address = loc_dom.xpath("//address/text()")
            raw_address = [e.strip() for e in raw_address if e.strip()]
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "US"
            phone = raw_address[-1]
            location_type = ""
            latitude = loc_dom.xpath("//@data-lat")[0]
            longitude = loc_dom.xpath("//@data-lng")[0]
            hoo = loc_dom.xpath(
                '//div[@id="office-hours"]/ul[@class="hours-list list-unstyled mb-0"]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type=location_type,
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
