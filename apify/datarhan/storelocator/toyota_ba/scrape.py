from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_urls = [
        "https://www.toyota.ba/contact/dealers/list",
        "https://www.toyota.bg/contact/dealers/list",
        "https://www.toyota.hr/contact/dealers/list",
        "https://www.toyota.si/contact/dealers/list",
    ]
    domain = "toyota.ba"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="dealer-details"]')
        for poi_html in all_locations:
            page_url = poi_html.xpath('.//a[@data-gt-action="view-dealer"]/@href')
            page_url = page_url[0] if page_url else ""
            if page_url and "http" not in page_url:
                page_url = "https://" + page_url
            location_name = poi_html.xpath(".//h2/text()")[0]
            raw_address = poi_html.xpath('.//li[@class="address"]/text()')[0]
            country_code = url.split("/")[2].split(".")[-1]
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
            phone = (
                phone.split("Prodaja: ")[-1]
                .split("Ser")[0]
                .split("жби ")[-1]
                .split("ja:")[-1]
                .split(",")[0]
                .split(";")[0]
            )
            latitude = ""
            longitude = ""
            if page_url:
                loc_response = session.get(page_url, headers=hdr)
                loc_dom = etree.HTML(loc_response.text)
                latitude = loc_dom.xpath("//@data-lat")
                latitude = latitude[0] if latitude else ""
                longitude = loc_dom.xpath("//@data-lng")
                longitude = longitude[0] if longitude else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address.split(" - ")[0],
                city=raw_address.split(" - ")[-1],
                state="",
                zip_postal="",
                country_code=country_code,
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
