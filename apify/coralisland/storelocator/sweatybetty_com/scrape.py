# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sweatybetty.com/shop-finder"
    domain = "sweatybetty.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="store-link"]/@href')
    for page_url in all_locations:
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="store-locator-details"]//h1/text()'
        )
        if not location_name:
            location_name = loc_dom.xpath('//p[@class="title"]/text()')
        location_name = location_name[0]
        raw_data = loc_dom.xpath(
            '//div[@class="small-6 medium-3 large-3 columns main-details"]/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[contains(@class, "store-details")]/p/text()'
            )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = ", ".join([e for e in " ".join(raw_data[:-1]).split()]).replace(
            "Nordstrom,,", ""
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if not street_address:
            street_address = raw_data[0]
        else:
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else ""
        hoo = []
        hours = loc_dom.xpath("//div[@data-day]")
        for h in hours:
            day = h.xpath(".//b/text()")[0]
            opens = h.xpath("@data-open")[0]
            closes = h.xpath("@data-close")[0]
            hoo.append(f"{day} {opens} - {closes}")
        hoo = " ".join(hoo)
        phone = loc_dom.xpath('//p[@class="phone"]/a/text()')
        phone = phone[0] if phone else ""
        if not phone:
            phone = raw_data[-1]
        state = addr.state
        zip_code = addr.postcode
        if state:
            if state.lower() == "m3":
                zip_code += " " + state
                state = ""
            if len(state) == 3:
                zip_code += " " + state
                state = ""
        if not zip_code and len(phone) == 7:
            zip_code = phone
            phone = ""
        country_code = addr.country
        city = addr.city
        if city == "Hong":
            city = "Hong Kong"
            country_code = "Hong Kong"
        phone = phone.split("Ask")[0].split("Phone:")[-1].strip()
        if not country_code and "Hong Kong" in phone:
            country_code = "Hong Kong"
            phone = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=page_url.split("=")[-1],
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_address,
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
