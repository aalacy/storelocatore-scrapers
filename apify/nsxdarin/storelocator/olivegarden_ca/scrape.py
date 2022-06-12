from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("olivegarden_ca")
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    urls = []
    url = "https://www.olivegarden.ca/ca-locations-sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>" in line:
            urls.append(line.split("<loc>")[1].split("<")[0])
    for url_store in urls:
        with SgChrome() as driver:
            driver.get(url_store)
            driver.implicitly_wait(30)
            wait_xpath = '//*[@id="/locations/location-search"]'
            WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, wait_xpath))
            )
            time.sleep(5)
            location_raw_data = driver.page_source
        locator_domain_name = "olivegarden.ca"
        tree = html.fromstring(location_raw_data)
        json_raw_data = tree.xpath('//script[@type="application/ld+json"]/text()')
        json_clean = "".join(json_raw_data).replace("\n", "")
        logger.info(("\nParsing data for: %s\n" % url_store))
        logger.info(("\nParsing data from.... \n%s\n" % json_clean))
        json_data = json.loads(json_clean)
        purl = json_data["url"] or "<MISSING>"
        website = locator_domain_name
        name = json_data["name"] or "<MISSING>"
        add = json_data["address"]["streetAddress"].strip() or "<MISSING>"
        city = json_data["address"]["addressLocality"].strip() or "<MISSING>"
        state = json_data["address"]["addressRegion"].strip() or "<MISSING>"
        country = json_data["address"]["addressCountry"] or "<MISSING>"
        zc = json_data["address"]["postalCode"].strip() or "<MISSING>"
        store = json_data["branchCode"] or "<MISSING>"
        phone = json_data["telephone"].strip() or "<MISSING>"
        typ = json_data["@type"] or "<MISSING>"
        lat = json_data["geo"]["latitude"] or "<MISSING>"
        lng = json_data["geo"]["longitude"] or "<MISSING>"
        hoo = json_data["openingHours"]
        if hoo:
            hoo = "; ".join(hoo)
            hours = hoo
        else:
            hours = "<MISSING>"
        if "saskatoon/saskatoon/4349" in url_store:
            hours = "Sun-Sat: 11:00AM-10:00PM"
        yield SgRecord(
            locator_domain=website,
            page_url=purl,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
