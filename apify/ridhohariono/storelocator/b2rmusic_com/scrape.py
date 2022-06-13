from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re


DOMAIN = "b2rmusic.com"
BASE_URL = "https://www.b2rmusic.com"
LOCATION_URL = "https://www.b2rmusic.com/browse-locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 200:
        soup = bs(req.content, "lxml")
    else:
        return False
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.results table tr.row")
    for row in contents:
        location_name = row.find("td").text.strip()
        page_url = row.find("a")["href"]
        if not page_url or page_url == LOCATION_URL:
            page_url = (
                "https://" + location_name.lower().replace(" ", "") + ".b2rmusic.com"
            )
        store = pull_content(page_url)
        if not store:
            page_url = LOCATION_URL
            addr = (
                row.find("a", {"href": re.compile(r"maps.*")})["href"]
                .split("&q=")[1]
                .replace("+", " ")
                .split(",")
            )
            street_address = addr[0].strip()
            city = addr[1].strip()
            state = addr[2].strip()
            zip_postal = addr[3].strip()
            phone = row.find_all("td")[-1].text.strip() or MISSING
            hours_of_operation = MISSING
            latitude = MISSING
            longitude = MISSING
        else:
            street_address = row.find("a", {"href": re.compile(r"maps.*")}).text.strip()
            city = store.find("span", {"itemprop": "addressLocality"}).text.strip()
            state = store.find("span", {"itemprop": "addressRegion"}).text.strip()
            zip_postal = store.find("span", {"itemprop": "postalCode"}).text.strip()
            phone = store.find("span", {"itemprop": "telephone"}).text.strip()
            hours_of_operation = re.sub(
                r",?\s+?\(.*\)|Hours of Operation,?",
                "",
                store.find("b", text="Hours of Operation").parent.get_text(
                    strip=True, separator=","
                ),
            )
            try:
                map_link = store.find(
                    "a", {"href": re.compile(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)")}
                )["href"]
                latitude, longitude = get_latlong(map_link)
            except:
                latitude = MISSING
                longitude = MISSING
        country_code = "US"
        location_type = MISSING
        store_number = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
