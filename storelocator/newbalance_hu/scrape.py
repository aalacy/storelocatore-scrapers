from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://newbalance.hu/"
urls = {
    "hu": "https://newbalance.hu/",
    "cz": "https://newbalance.cz/",
    "sk": "https://newbalance.sk/",
}

api_url = "api/frontend/sk/snippet/many"


def fetch_data():
    with SgChrome() as driver:
        for country_code, base_url in urls.items():
            driver.get(base_url)
            time.sleep(5)
            _ = bs(driver.page_source, "lxml")
            hours = list(
                _.select_one('span[itemprop="telephone"]')
                .find_parent()
                .stripped_strings
            )[-1]
            yield SgRecord(
                page_url=base_url,
                location_name="New Balance Store",
                country_code=country_code,
                phone=_.select_one('span[itemprop="telephone"]').text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PHONE}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
