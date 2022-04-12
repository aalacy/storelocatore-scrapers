import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests(verify_ssl=False)
    start_url = "https://www.thebetterhealthstore.com/pointofsale/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="place US"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")[1]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h3/a/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="details"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if ";" in raw_data[0]:
            raw_address = raw_data[0].replace(";", ",")
        else:
            raw_address = " ".join(raw_data).split("☎")[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.split()[0]
        country_code = addr.country
        phone = raw_data[-1][2:]
        hoo = []
        hoo = [e for e in loc_dom.xpath("//p/text()") if "Hours:" in e]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = hoo[0].split("Hours:")[-1].strip() if hoo else "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[-1].split("ll=")[-1].split("&")[0].split(",")
        )
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        else:
            try:
                geo = (
                    loc_dom.xpath('//a[contains(@href, "/maps/")]/@href')[0]
                    .split("/@")[-1]
                    .split(",")[:2]
                )
                latitude = geo[0]
                longitude = geo[1]
            except:
                with SgFirefox() as driver:
                    driver.get(store_url)
                    driver.switch_to.frame(
                        driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
                    )
                    loc_dom = etree.HTML(driver.page_source)
                geo = (
                    loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                    .split("/@")[-1]
                    .split(",")[:2]
                )
                latitude = geo[0]
                longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
