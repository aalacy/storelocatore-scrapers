from lxml import etree
from urllib.parse import urljoin
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl

from sglogging import sglog

domain = "aldi.pl"
log = sglog.SgLogSetup().get_logger(logger_name=domain)


def fetch_data():

    start_url = "https://www.yellowmap.de/partners/AldiNord/Html/Poi.aspx"

    search_url = "https://www.yellowmap.de/Partners/AldiNord/Search.aspx?BC=ALDI|ALDN&Search=1&Layout2=True&Locale=pl-PL&PoiListMinSearchOnCountZeroMaxRadius=50000&SupportsStoreServices=true&Country=PL&Zip={}&Town=&Street=&Radius=100000"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.POLAND], expected_search_radius_miles=10
    )

    for code in all_codes:
        sleep(uniform(5, 9))
        session = SgRequests(retries_with_fresh_proxy_ip=1)
        log.info(f"API Crawl: {search_url.format(code)}")
        response = session.get(search_url.format(code))
        log.info(f"First Response: {response}")
        session_id = str(response.url.raw[-1]).split("=")[-1]
        hdr = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        }
        dom = etree.HTML(
            response.text.replace('<?xml version="1.0" encoding="utf-8"?>', "")
        )
        option = dom.xpath('//select[@name="Loc"]/option/@value')
        loc = option[0] if option else ""

        frm = {
            "SessionGuid": session_id,
            "View": "",
            "ClearParas": "AdminUnitID,AdminUnitName,WhereCondition",
            "ClearGroups": "GeoMap,MapNav",
            "Locale": "es-ES",
            "Loc": loc,
        }

        response = session.post(start_url, headers=hdr, data=frm)
        log.info(f"Second Response: {response}")
        dom = etree.HTML(
            response.text.replace('<?xml version="1.0" encoding="utf-8"?>', "")
        )

        all_locations = dom.xpath('//tr[@class="ItemTemplate"]')

        all_locations += dom.xpath('//tr[@class="AlternatingItemTemplate"]')

        next_page = dom.xpath('//div[@class="ButtonPageNextOn"]/a/@href')
        log.info(f"total page: {len(next_page)}")
        while next_page:
            next_page_link = urljoin(start_url, next_page[0])
            log.info(f"Next page link: {next_page_link}")
            response = session.get(next_page_link)
            log.info(f"Third Response: {response}")
            dom = etree.HTML(
                response.text.replace('<?xml version="1.0" encoding="utf-8"?>', "")
            )
            all_locations += dom.xpath('//td[@class="ItemTemplateColumnLocation"]')
            all_locations += dom.xpath(
                '//td[@class="AlternatingItemTemplateColumnLocation"]'
            )
            next_page = dom.xpath('//div[@class="ButtonPageNextOn"]/a/@href')

        for poi_html in all_locations:
            location_name = poi_html.xpath('.//p[@class="PoiListItemTitle"]/text()')[0]
            raw_adr = poi_html.xpath(".//address/text()")
            raw_adr = [e.strip() for e in raw_adr]
            addr = parse_address_intl(" ".join(raw_adr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hoo = poi_html.xpath('.//td[contains(@class,"OpeningHours")]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.aldi.pl/informacje-dla-klienta/wyszukiwarka-sklepu.html",
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=SgRecord.MISSING,
                zip_postal=addr.postcode,
                country_code="PL",
                store_number=SgRecord.MISSING,
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    log.info("Started Crawling")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)
            count = count + 1

    log.info(f"Total Rows: {count}")


if __name__ == "__main__":
    scrape()
