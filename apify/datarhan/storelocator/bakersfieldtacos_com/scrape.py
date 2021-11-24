import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.bakersfieldtacos.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h2/text()")[0]

        raw_data = poi_html.xpath(".//p/a/text()")
        addr = parse_address_intl(" ".join(raw_data[:-1]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1]
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//p/a/@href")[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath('.//ul[@class="list-unstyled"]/li/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Call for")[0].strip() if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
