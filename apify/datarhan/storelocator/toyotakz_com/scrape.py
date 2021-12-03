from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotakz.com/dealers/toyota-dealers"
    domain = "toyotakz.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//section[div[div[@class="title-h5"]]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="title-h5"]/span/text()')[0]
        if "Тойота Сервис" in location_name:
            continue
        raw_address = poi_html.xpath(
            './/div[@class="title-h5"]/following-sibling::p[1]//text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()][0]
        street_address = raw_address.split(" - ")[0]
        city = raw_address.split(" - ")[-1]
        if street_address.startswith("г."):
            city = street_address.split(", ")[0].replace("г.", "")
            street_address = ", ".join(street_address.split(", ")[1:])
        phone = poi_html.xpath(".//p[a]/text()")[1].strip()
        if not phone:
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        page_url = poi_html.xpath(".//p/a/@href")[-1]
        geo = poi_html.xpath(".//p/a/@href")[0]
        latitude = ""
        longitude = ""
        if "2gis" in geo:
            geo = (
                poi_html.xpath(".//p/a/@href")[0]
                .split("center")[-1]
                .split("%2F")[1]
                .split("%2C")
            )
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="KZ",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
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
