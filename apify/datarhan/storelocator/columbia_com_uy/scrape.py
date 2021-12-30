# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.columbia.com.uy/tiendas#!Uruguay"
    domain = "columbia.com.uy"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-pais]")
    for poi_html in all_locations:
        country_code = poi_html.xpath("@data-pais")[0]
        city = poi_html.xpath("@data-dpto")[0]
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        page_url = poi_html.xpath('.//a[@class="nom"]/@href')[0]
        raw_address = poi_html.xpath('.//span[@class="dir"]/span/text()')[0]
        location_name = poi_html.xpath('.//a[@class="nom"]/text()')[0]
        phone = poi_html.xpath('.//span[@class="tel"]/text()')[0].split(":")[-1].strip()
        if phone == ".":
            phone = ""
        hoo = poi_html.xpath('.//span[@class="hor"]//text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address.split(" - ")[0].split(",")[0],
            city=city,
            state="",
            zip_postal="",
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
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
