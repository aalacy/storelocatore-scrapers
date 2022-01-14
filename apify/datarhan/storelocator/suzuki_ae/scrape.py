from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://suzuki.ae/locations/abu-dhabi/showroom"
    domain = "suzuki.ae"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@class="w-full block hover:bg-gray-200  py-2 md:py-4"]/@href'
    )
    all_locations.append(start_url)
    for page_url in all_locations:
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="text-3xl mb-5 suzuki-bold"]/text()'
        )[0]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath(
            '//div[@class="info grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-5"]/div[2]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        geo = (
            loc_dom.xpath('//a[@class="theme-link text-base"]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address="",
            city="",
            state="",
            zip_postal="",
            country_code="AE",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0].split("=")[-1],
            longitude=geo[1],
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
