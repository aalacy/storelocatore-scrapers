from lxml import etree
from urllib.parse import urljoin
from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import re


DOMAIN = "marcs.com"

MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


@retry(stop=stop_after_attempt(3))
def get(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    return session.get(url, headers=headers)


@retry(stop=stop_after_attempt(3))
def post(url, data):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-microsoftajax": "Delta=true",
        "x-requested-with": "XMLHttpRequest",
    }
    return session.post(url, data, headers=headers)


def fetch_data():
    # Your scraper here
    start_url = "https://www.marcs.com/Store-Finder"
    response = get(start_url)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        expected_search_radius_miles=10,
        max_search_results=None,
    )
    for code in all_codes:
        formdata = {
            "manScript": "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$UpdatePanel1|p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$submit",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "lng": "en-US",
            "p$lt$ctl01$SmartSearchBox$txtWord": "",
            "p$lt$ctl02$SmartSearchBox1$txtWord_exWatermark_ClientState": "",
            "p$lt$ctl02$SmartSearchBox1$txtWord": "",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$address": str(code),
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$radius": "50",
            "__VIEWSTATEGENERATOR": viewgen,
            "__SCROLLPOSITIONX": "0",
            "__SCROLLPOSITIONY": "0",
            "__ASYNCPOST": "true",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$submit": "Submit",
        }

        response = post(start_url, formdata)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(@id, "storelink")]/@href')
        response = get(start_url)
        dom = etree.HTML(response.text)
        viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
        viewgen = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath('//h1[@class="display-text"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@class="col-half sm-col-full"]/p/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        city = address_raw[1].split(", ")[0]
        state = address_raw[1].split(", ")[-1].split()[0]
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = address_raw[-1].split(": ")[-1]
        location_type = "<MISSING>"
        latitude = re.findall("lat = \\'(.+?)\\'", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("lng = \\'(.+?)\\'", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[h3[contains(text(), "Store Hours")]]/text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                }
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
