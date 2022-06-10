from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "peterpiperpizza.com"
SITE_MAP = "https://locations.peterpiperpizza.com/sitemap.xml"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except:
        log.info("[RETRY] Pull content => " + url)
        pull_content(url)
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = pull_content(SITE_MAP).find_all("loc")
    for row in page_urls:
        page_url = row.text.strip()
        check_url = page_url.replace("https://", "").replace("/es/", "").split("/")
        if len(check_url) < 4:
            continue
        store = pull_content(page_url)
        location_name = (
            store.find("h1", id="location-name").text.replace("\n", " ").strip()
        )
        addr = store.find("address", id="address")
        street_address = addr.find("meta", {"itemprop": "streetAddress"})[
            "content"
        ].strip()
        city = addr.find("meta", {"itemprop": "addressLocality"})["content"].strip()
        state = addr.find("abbr", {"itemprop": "addressRegion"}).text.strip()
        zip_postal = addr.find("span", {"itemprop": "postalCode"}).text.strip()
        country_code = addr.find("abbr", {"itemprop": "addressCountry"}).text.strip()
        phone = store.find("div", id="phone-main").text.strip()
        store_number = store.find("div", id="js-ceccookie")["data-storeid"]
        try:
            hours_of_operation = (
                store.find("table", {"class": "c-hours-details"})
                .find("tbody")
                .get_text(strip=True, separator=" ")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        latitude = store.find("meta", {"itemprop": "latitude"})["content"]
        longitude = store.find("meta", {"itemprop": "longitude"})["content"]
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
