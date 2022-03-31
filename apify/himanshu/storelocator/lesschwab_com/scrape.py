import json
from lxml import etree
from urllib.parse import urljoin
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "lesschwab.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data():
    session = SgRequests()
    scraped_urls = []
    start_url = "https://www.lesschwab.com/stores/?latitude={}&longitude={}"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[@title="Store Details"]/@href')
        for url in list(set(all_locations)):
            page_url = urljoin(start_url, url)
            if page_url in scraped_urls:
                continue
            scraped_urls.append(page_url)
            log.info("Pull content => " + page_url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')
            location_name = (
                loc_dom.xpath('//h2[@class="storeDetails__storeName"]/text()')[0]
                .replace("\n", "")
                .strip()
            )
            if poi:
                poi = json.loads(poi[0])
                hoo = loc_dom.xpath(
                    '//section[@class="storeDetails__hoursInformation"]/div/p/text()'
                )
                hoo = " ".join(hoo).replace("By Appointment Only", "").strip()
                street_address = poi["address"]["streetAddress"]
                city = poi["address"]["addressLocality"]
                state = poi["address"]["addressRegion"]
                zip_code = poi["address"]["postalCode"]
                phone = poi["telephone"]
                loc_type = poi["@type"]
            else:
                street_address = (
                    loc_dom.xpath('//div[@class="storeDetails__streetName"]/text()')[0]
                    .replace("\n", "")
                    .strip()
                )
                raw_address = loc_dom.xpath(
                    '//div[@class="storeSearch__resultsSection"]//address[@class="storeDetails__address"]//div[@class="storeDetails__zip"]/text()'
                )
                if raw_address:
                    raw_address = raw_address[0].strip().split(", ")
                    city = raw_address[0]
                    state = raw_address[-1].split()[0]
                    zip_code = raw_address[-1].split()[0]
                    if len(zip_code) == 2:
                        zip_code = ""
                else:
                    raw_address = loc_dom.xpath("//div[@data-store-id]//address/text()")
                    raw_address = [e.strip() for e in raw_address if e.strip()]
                    city = raw_address[-1].split(", ")[0]
                    state = raw_address[-1].split(", ")[-1].split()[0]
                    zip_code = raw_address[-1].split(", ")[-1].split()[-1]
                loc_type = ""
                hoo = list(
                    set(
                        loc_dom.xpath(
                            '//h6[contains(text(), "Hours")]/following-sibling::div[1]/p/text()'
                        )
                    )
                )
                hoo = " ".join(hoo).replace("By Appointment Only", "").strip()
            print(hoo)
            store_number = loc_dom.xpath("//div[@data-store-id]/@data-store-id")[0]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type=loc_type,
                latitude="",
                longitude="",
                hours_of_operation=hoo,
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
