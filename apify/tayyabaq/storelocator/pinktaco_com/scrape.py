from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://pinktaco.com/locations/"
    domain = "pinktaco.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="location"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//div[contains(text(), "COMING SOON!")]'):
            continue

        location_name = loc_dom.xpath('//meta[@property="og:title"]/@content')[0]
        raw_data = loc_dom.xpath('//div[@class="details"]//text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_adr = raw_data[1].split(", ")
        phone = raw_data[2]
        if len(raw_adr) == 1:
            raw_adr = ", ".join([raw_adr[0], raw_data[2]]).split(", ")
            phone = raw_data[3]
        hoo = (
            " ".join(raw_data[4:])
            .split("Brunch Hours")[0]
            .strip()
            .split("Happy Hour")[0]
            .replace("Restaurant Hours ", "")
        )
        if location_name == "Location":
            location_name = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_adr[0],
            city=raw_adr[1],
            state=raw_adr[-1].split()[0],
            zip_postal=raw_adr[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=loc_dom.xpath("//@data-lat")[0],
            longitude=loc_dom.xpath("//@data-lng")[0],
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
