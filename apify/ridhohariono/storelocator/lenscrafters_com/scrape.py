from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


DOMAIN = "lenscrafters.com"
SITE_MAP = "https://local.lenscrafters.com/sitemap.xml"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITE_MAP)
    contents = soup.select("loc")
    for row in contents:
        page_url = row.text
        if (
            "https://local.lenscrafters.com/" in page_url
            and "https://local.lenscrafters.com/eyedoctors" not in page_url
        ):
            count = page_url.count("/")
            if count != 5:
                continue
            store = pull_content(page_url)
            try:
                hours_today = store.find(
                    "div", {"class": "Hero-hoursToday"}
                ).text.strip()
                if "Coming Soon" in hours_today:
                    continue
            except:
                pass
            location_name = store.find("h1", id="location-name").text.strip()
            street_address = store.find("meta", {"itemprop": "streetAddress"})[
                "content"
            ]
            city = store.find("span", {"class": "c-address-city"}).text.strip()
            try:
                state = store.find("abbr", {"class": "c-address-state"}).text.strip()
            except:
                state = MISSING
            try:
                zip_postal = store.find(
                    "span", {"class": "c-address-postal-code"}
                ).text.strip()
            except:
                zip_postal = MISSING
            country_code = store.find("address", id="address")["data-country"]
            try:
                phone = store.find("div", id="phone-main").text.strip()
            except:
                phone = MISSING
            location_type = MISSING
            store_number = MISSING
            hours_of_operation = (
                store.find("table", {"class": "c-hours-details"})
                .find("tbody")
                .get_text(strip=True, separator=" ")
                .strip()
            )
            latitude = store.find("meta", {"itemprop": "latitude"})["content"]
            longitude = store.find("meta", {"itemprop": "longitude"})["content"]
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
