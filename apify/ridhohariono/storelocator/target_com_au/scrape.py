from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "target.com.au"
LOCATION_URL = "https://www.target.com.au/store-finder"
BASE_URL = "https://www.target.com.au"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def pull_content(url, num=0):
    num += 1
    session = SgRequests()
    log.info("Pull content => " + url)
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except Exception as e:
        if num < 3:
            return pull_content(url, num)
        raise e
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    states = soup.select("ul.store-states a")
    for row in states:
        stores = pull_content(BASE_URL + row["href"]).select(
            "td[headers='store-opening'] a"
        )
        for store_link in stores:
            page_url = BASE_URL + store_link["href"]
            store = pull_content(page_url)
            location_name = (
                store.find("h4", {"class": "store-heading"})
                .text.replace("Target –", "")
                .strip()
            )
            try:
                store.find("span", {"itemprop": "streetAddress"}).find(
                    "strong"
                ).decompose()
            except:
                pass
            street_address = (
                store.find("span", {"itemprop": "streetAddress"})
                .get_text(strip=True, separator=",")
                .strip()
                .rstrip(",")
            )
            city = store.find("span", {"itemprop": "addressLocality"}).text.strip()
            state = store.find("span", {"itemprop": "addressRegion"}).text.strip()
            zip_postal = store.find("span", {"itemprop": "postalCode"}).text.strip()
            country_code = "AU"
            phone = store.find("span", {"itemprop": "telephone"}).text.strip()
            location_type = MISSING
            hours_of_operation = (
                store.find("dl", {"class": "this-week"})
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .strip()
            )
            store_number = store_link["href"].split("/")[-1]
            latlong = store.find("div", {"class": "imap store-map"})
            latitude = latlong["data-lat"]
            longitude = latlong["data-lng"]
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
