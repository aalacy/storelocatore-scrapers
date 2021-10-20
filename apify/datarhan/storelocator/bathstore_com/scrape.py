import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bathstore.com/stores"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//li[@class="storesList_locations"]/a/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath(
            '//h3[@class="storeDetailMap_locationName_title"]/text()'
        )[0]
        raw_address = loc_dom.xpath('//div[@class="storeDetailMap_address"]/p/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        city = raw_address[-2].split(", ")[-1].strip()
        if city == ",":
            city = ""
        street_address = ", ".join(raw_address[:-2])
        if "," in raw_address[-2] and raw_address[-2].split(",")[0] != city:
            street_address += ", " + raw_address[-2].split(",")[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        street_address = street_address.replace(",,", "")
        phone = loc_dom.xpath(
            '//div[@class="storeDetailMap_locationInformation"]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else ""
        geo = loc_dom.xpath("//@data-latlong")[0].split(",")
        hoo = loc_dom.xpath(
            '//li[@class="storeDetailMap_openingTime_item"]/span/text()'
        )
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=raw_address[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=" ".join(raw_address),
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
