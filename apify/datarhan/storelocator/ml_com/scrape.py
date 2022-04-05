import json
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

DOMAIN = "ml.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data():
    session = SgRequests()
    scraped_urls = []
    start_url = "https://fa.ml.com/find-an-advisor/locator/api/InternalSearch"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    usr_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    body = '{"Locator":"MER-WM-Offices","PostalCode":"%s","Company":null,"ProfileTypes":"Branch","DoFuzzyNameSearch":0,"SearchRadius":"50"}'

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=50,
    )

    for code in all_codes:
        response = session.post(start_url, data=body % code, headers=hdr)
        if not response.text:
            continue
        data = json.loads(response.text)
        if not data.get("Results"):
            continue
        for poi in data["Results"]:
            try:
                store_url = "https:" + poi["XmlData"]["parameters"]["Url"]
            except:
                continue
            if store_url in scraped_urls:
                continue
            log.info("Pull content => " + store_url)
            scraped_urls.append(store_url)
            location_name = poi["Company"]
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            city = poi["City"]
            state = poi["Region"]
            zip_code = poi["PostalCode"]
            country_code = poi["Country"]
            store_number = poi["ProfileId"]
            phone = poi["XmlData"]["parameters"].get("LocalNumber")
            latitude = poi["GeoLat"]
            longitude = poi["GeoLon"]
            location_type = poi["ProfileType"]

            store_response = session.get(store_url, headers=usr_agent)
            if store_response.status_code != 200:
                continue
            store_dom = etree.HTML(store_response.text)
            hours_of_operation = ""
            if store_dom is not None:
                hours_of_operation = store_dom.xpath(
                    '//div[@id="more-hours"]//ul/li/text()'
                )
                if not hours_of_operation:
                    hours_of_operation = store_dom.xpath(
                        '//li[@class="more-hours"]//span/text()'
                    )
                hours_of_operation = (
                    (" ".join(hours_of_operation) if hours_of_operation else "")
                    .replace("Hours of Operation:", "")
                    .strip()
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
