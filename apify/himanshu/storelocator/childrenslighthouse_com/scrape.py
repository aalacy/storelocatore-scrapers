import re
import json
from lxml import etree
from urllib.parse import urljoin
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="childrenslighthouse.com")


def fetch_data():
    start_url = "https://childrenslighthouse.com/find-a-daycare"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_states = dom.xpath('//a[@class="region_link"]/@href')
        for url in all_states:
            url = urljoin(start_url, url)
            response = session.get(url, headers=hdr)
            dom = etree.HTML(response.text)
            if "near-me" in str(response.url):
                all_locations += dom.xpath(
                    '//a[@class="region_location no_highlight"]/@href'
                )
            else:
                all_locations.append(url)

        for url in all_locations:
            page_url = urljoin(start_url, url)
            log.info(page_url)
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)

            if (
                loc_dom.xpath('//div[@class="nav_coming_soon"]')
                or "Coming Soon" in loc_response.text
            ):
                continue
            poi = loc_dom.xpath('//script[contains(text(), "addressRegion")]/text()')
            if poi:
                poi = json.loads(poi[0])
                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code=SgRecord.MISSING,
                    store_number=SgRecord.MISSING,
                    phone=poi["telePhone"],
                    location_type=poi["@type"],
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
                    hours_of_operation=poi["openingHours"],
                )
            else:
                location_name = loc_dom.xpath(
                    '//h2[@class="contact_location_name meri"]/div/text()'
                )[0]
                street_address = loc_dom.xpath(
                    '//div[@class="contact_address contact_info"]/a/div/text()'
                )[0]
                raw_adr = loc_dom.xpath('//div[@class="conact_address_line_2"]/text()')[
                    0
                ].split(", ")
                phone = loc_dom.xpath('//a[@class="tel_link"]/text()')
                phone = phone[0] if phone else SgRecord.MISSING
                hours_of_operation = loc_dom.xpath(
                    '//div[@class="far fa-clock icon"]/following-sibling::div/text()'
                )[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=raw_adr[0],
                    state=raw_adr[1].split()[0],
                    zip_postal=raw_adr[1].split()[-1],
                    country_code=SgRecord.MISSING,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
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
