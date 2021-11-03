from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_urls = [
        "https://www.solasalonstudios.com/locations",
        "https://www.solasalonstudios.ca/locations",
    ]
    domain = "solasalonstudios.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//input[@name="marker"]')
        for poi_html in all_locations:
            store_url = urljoin(start_url, poi_html.xpath("@data-url")[0])
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi_html.xpath("@data-name")[0]
            raw_address = poi_html.xpath("@data-address")[0].split("<br>")
            country_code = "CA"
            if ".com" in start_url:
                country_code = "US"
            geo = poi_html.xpath("@value")[0].split(", ")
            phone = loc_dom.xpath('//a[@class="location-phone-number"]/text()')
            phone = phone[0].strip() if phone else SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[-1].split(", ")[0],
                state=raw_address[-1].split(", ")[-1].split()[0],
                zip_postal=" ".join(raw_address[-1].split(", ")[-1].split()[1:]),
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=SgRecord.MISSING,
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
