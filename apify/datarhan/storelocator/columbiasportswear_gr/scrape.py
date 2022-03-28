from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.columbiasportswear.gr/el/plirofories/katastimata/"
    domain = "columbiasportswear.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="partner-list"]/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        location_type = poi_html.xpath('.//li[@class="type"]/div/text()')[0]
        if location_type == "Columbia Retailer" or location_type == "Columbia Offices":
            continue
        street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')[
            0
        ].strip()[:-1]
        state = (
            poi_html.xpath('.//span[@class="area"]/text()')[0].strip().replace(",", "")
        )
        city = (
            poi_html.xpath('.//span[@class="city"]/text()')[0].strip().replace(",", "")
        )
        zip_code = poi_html.xpath('.//span[@class="postal-code"]/text()')[0]
        phone = poi_html.xpath('.//li[@class="phone "]/a/text()')[0]
        latitude = poi_html.xpath(".//@data-latitude")[0]
        longitude = poi_html.xpath(".//@data-longitude")[0]
        hoo = poi_html.xpath('.//li[@class="description icon-open-hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="GR",
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
