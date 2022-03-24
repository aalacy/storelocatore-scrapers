# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://directory.ageuk.org.uk/charity-shops/?s={}"
    domain = "ageuk.org.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[@class="ldShop-link"]/@href')
        next_page = dom.xpath('//a[contains(text(), "View more shops")]/@href')
        while next_page:
            response = session.get(urljoin(start_url, next_page[0]))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="ldShop-link"]/@href')
            next_page = dom.xpath('//a[contains(text(), "View more shops")]/@href')

        for page_url in list(set(all_locations)):
            page_url = urljoin(start_url, page_url)
            loc_response = session.get(page_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath(
                '//h1[@class="localDirectoryHeader-title"]/text()'
            )
            if not location_name:
                continue
            location_name = location_name[0]
            raw_address = loc_dom.xpath("//address/text()")
            raw_address = [e.strip() for e in raw_address if e.strip()]
            phone = loc_dom.xpath('//span[@class="telNo-desktop"]/text()')
            phone = phone[0] if phone else ""
            hoo = loc_dom.xpath(
                '//dt[contains(text(), "Opening times")]/following-sibling::dd//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo).replace("Opening times", "").strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1],
                state="",
                zip_postal=raw_address[-1],
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
