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

    start_url = "https://www.lexus.cz/contact/retailers"
    domain = "lexus.cz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "contact/retailers/")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        if "lexus-pruhonice" not in page_url:
            data = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
            poi = json.loads(data)
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            zip_code = poi["address"]["postalCode"]
            phone = poi["telephone"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            location_name = loc_dom.xpath('//div[@class="dealer-heading"]/div/text()')[
                0
            ]
            raw_address = loc_dom.xpath(
                '//div[@class="bottom-contact-item col-lg-8"]/div/text()'
            )
            raw_address = [e.strip() for e in raw_address if e.strip()]
            street_address = raw_address[0]
            city = " ".join(raw_address[1].split()[2:])
            zip_code = " ".join(raw_address[1].split()[:2])
            phone = (
                loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
                .split(":")[-1]
                .strip()
            )
            location_type = "AutomotiveBusiness"
            geo = loc_dom.xpath("//@data-location")[0].split(",")
            latitude = geo[1]
            longitude = geo[0]

        hoo = loc_dom.xpath(
            '//div[contains(text(), "ShowRoom")]/following-sibling::ul//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="CZ",
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
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
