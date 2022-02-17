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

    domain = "arcb.com"
    start_url = "https://arcb.com/ajax/apipassthrough/passthrough.html"

    session.get("https://arcb.com/shipping-tools/international-coverage-area")
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Bearer DHL6KC8Y",
        "X-Visitor-Session": "9AE3C720B68A9B7C",
        "X-ABF-API-Destination": "https://apps.abf.com/api/global-network/global-locations",
        "DNT": "1",
    }
    session.get("https://arcb.com/user/json2", headers=hdr)

    data = session.get(start_url, headers=hdr).json()
    for poi in data["locations"]:
        if poi["physicalCountry"] in ["United States", "Canada"]:
            continue
        page_url = "https://arcb.com/shipping-tools/international-coverage-area"
        street_address = poi["physicalAddress1"]
        if poi["physicalAddress2"]:
            street_address += ", " + poi["physicalAddress2"]
        if not street_address:
            street_address = poi["mailingAddress"]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["displayName"],
            street_address=street_address,
            city=poi["physicalCity"],
            state=poi["physicalState"],
            zip_postal=poi["physicalZip"],
            country_code=poi["physicalCountry"],
            store_number=SgRecord.MISSING,
            phone=poi["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=SgRecord.MISSING,
        )

        yield item

    all_locations = []
    start_url = "https://arcb.com/coverage-area/us-shipping"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//nav[@id="block-coveragearealocalnav"]//a/@href')
    for url in all_urls:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="stations"]//a/@href')
        all_locations += dom.xpath(
            '//a[@class="expanded dropdown gtm" and contains(@href, "/coverage-area/")]/@href'
        )
        all_urls += dom.xpath(
            '//h2[contains(text(), "Canadian Service Centers")]/following-sibling::ul//a/@href'
        )

    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        raw_adr = loc_dom.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::div/text()'
        )[:3]
        phone = loc_dom.xpath(
            '//h4[contains(text(), "Phone Number")]/following-sibling::div/text()'
        )
        phone = phone[0] if phone else ""
        geo = re.findall(r"LatLng\((.+?)\);", loc_response.text)
        if not geo:
            continue
        geo = geo[0].split(", ")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=loc_dom.xpath("//h1/text()")[0],
            street_address=raw_adr[0],
            city=raw_adr[1].split(", ")[0],
            state=raw_adr[1].split(", ")[-1].split()[0],
            zip_postal=raw_adr[1].split(", ")[-1].split()[1],
            country_code=raw_adr[-1],
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=SgRecord.MISSING,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
