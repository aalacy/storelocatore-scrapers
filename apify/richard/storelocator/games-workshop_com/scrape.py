from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgselenium import SgChrome
from selenium.webdriver.common.by import By
import ssl
import time
from sglogging import sglog

ssl._create_default_https_context = ssl._create_unverified_context
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
locator_domain = "https://www.games-workshop.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):
    with SgChrome(user_agent=user_agent) as driver:
        api_urls = [
            "https://www.games-workshop.com/en-US/store/fragments/resultsJSON.jsp?latitude=40.2475923&radius=20000&longitude=-77.03341790000002",
            "https://www.games-workshop.com/en-GB/store/fragments/resultsJSON.jsp?latitude=53.2362&radius=500&longitude=-1.42718",
        ]
        for api_url in api_urls:
            driver.get(api_url)
            time.sleep(40)
            js = json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)[
                "locations"
            ]
            log.info(f"Total pages to crawl: {len(js)}")
            for j in js:

                page_url = f'https://www.games-workshop.com/en-US/{j.get("seoUrl")}'
                log.info(f"Crawling: {page_url}")
                location_name = j.get("name")
                street_address = j.get("address1")
                address_sub = j.get("address2")
                if address_sub:
                    street_address = f"{j.get('address1')} {j.get('address2')}".replace(
                        "None", ""
                    ).strip()
                postal = j.get("postalCode")
                country_code = j.get("country")
                city = j.get("city")
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                phone = j.get("telephone")
                store_number = (
                    str(j.get("id"))
                    .replace("store-gb-", "")
                    .replace("UK.C000", "")
                    .strip()
                )
                location_type = j.get("type")

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
