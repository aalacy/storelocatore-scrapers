# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.wererolling.com/locations"
    domain = "wererolling.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_adr = dom.xpath('//a[contains(@href, "maps")]/@href')
    all_poi = dom.xpath(
        '//p[@style="text-align:center;white-space:pre-wrap;" and strong]'
    )
    all_names = []
    all_phones = []
    for e in all_poi:
        name = e.xpath(".//strong/text()")[0]
        phone = e.xpath(".//strong/text()")[-1].split(":")[-1].strip()
        all_names.append(name)
        all_phones.append(phone)

    for i, adr_url in enumerate(all_adr):
        raw_adr = adr_url.split("/")[5].replace("+", " ").split(", ")
        geo = adr_url.split("/@")[-1].split(",")[:2]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.wererolling.com/locations",
            location_name=all_names[i],
            street_address=raw_adr[0],
            city=raw_adr[1],
            state=raw_adr[2].split()[0],
            zip_postal=raw_adr[2].split()[-1],
            country_code="",
            store_number="",
            phone=all_phones[i],
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
