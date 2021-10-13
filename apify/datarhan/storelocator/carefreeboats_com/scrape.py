# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import ssl
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()

    start_url = "https://carefreeboats.com/locations/"
    domain = "carefreeboats.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_places = dom.xpath('//section[@id="siteorigin-panels-builder-2"]//li/a/@href')
    all_places = [e for e in all_places if "/locations/" in e]
    for url in all_places:
        response = session.get(urljoin(start_url, url), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//a[contains(text(), "Locations")]/following-sibling::ul[1]//a/@href'
        )

    for page_url in list(set(all_locations)):
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="siteorigin-widget-tinymce textwidget"]/p/strong/text()'
        )
        location_name = location_name[0] if location_name else ""
        if not location_name:
            location_name = loc_dom.xpath("//h2/strong/text()")
            location_name = " ".join([e.strip() for e in location_name])
        raw_address = loc_dom.xpath('//i[@class="ion-location"]/following::text()')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="siteorigin-widget-tinymce textwidget" and h2[strong]]/p[1]/text()'
            )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="siteorigin-widget-tinymce textwidget" and p[strong]]/p[1]/text()'
            )
            raw_address = [" ".join([e.strip() for e in raw_address if e.strip()])]
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="siteorigin-widget-tinymce textwidget"]/p/text()'
            )[:2]
            raw_address = [" ".join([e.strip() for e in raw_address if e.strip()])]

        poi = loc_dom.xpath("//@data-options")
        if poi:
            poi = json.loads(poi[0])
            geo = poi["address"].split(", ")
            phone = ""
            if poi["markerPositions"]:
                phone = etree.HTML(poi["markerPositions"][0]["info"]).xpath(
                    "//a/text()"
                )
                phone = phone[0] if phone else ""
        else:
            with SgChrome() as driver:
                driver.get(page_url)
                sleep(15)
                try:
                    driver.switch_to.frame(
                        driver.find_element_by_xpath("//iframe[@class='lazyloaded']")
                    )
                    loc_dom = etree.HTML(driver.page_source)
                    geo = (
                        loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                        .split("/@")[-1]
                        .split(",")[:2]
                    )
                    phone = loc_dom.xpath('//a[contains(@href, "tel")]/@href')
                except Exception:
                    geo = ["", ""]
        if raw_address:
            raw_address = raw_address[0]
        else:
            raw_address = poi["markerPositions"][0]["place"]
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/@href')
            phone = phone[0].split(":")[-1] if phone else ""
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if len(geo) == 1:
            geo = ["", ""]
        if not street_address:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
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
