import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import lxml.html

DOMAIN = "o2fitnessclubs.com"
BASE_URL = "https://www.o2fitnessclubs.com"
LOCATION_URL = "https://www.o2fitnessclubs.com/locations"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    sel = lxml.html.fromstring(req.text)
    return soup, sel


def parse_hours(element):
    if not element:
        return MISSING
    days = [val.text for val in element.find_all("p", text=re.compile(r"day.*"))]
    hours = [
        val.text
        for val in element.find_all("h5", text=re.compile(r"\d{1,2}\s+am|pm|Closed"))
    ]
    hoo = []
    for i in range(len(days)):
        hoo.append(
            "{}: {}".format(days[i].replace("–", "-"), hours[i].replace("–", "-"))
        )
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup, sel = pull_content(LOCATION_URL)
    content = soup.find_all("div", {"class": "hs-accordion__item-content"})
    for row in content:
        stores = row.find("ul").find_all("a")
        for link in stores:
            if DOMAIN in link["href"]:
                store_urls.append(link["href"])
            else:
                store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def get_latlong(soup):
    content = soup.find("script", string=re.compile(r"center\:\s+\[(.*)\]"))
    if not content:
        return MISSING, MISSING
    latlong = re.search(r"center\:\s+\[(.*)\]", content.string).group(1).split(",")
    return latlong[1].strip(), latlong[0].strip()


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    for page_url in store_urls:
        page_url = page_url.replace("?hsLang=en", "")
        if "wilmington-mayfaire-town-center" in page_url:
            continue
        soup, sel = pull_content(page_url)
        comming_soon = soup.find("div", {"class": "location-description"})
        if comming_soon and "coming soon" in comming_soon.text.strip().lower():
            continue

        if (
            "coming soon"
            in "".join(
                sel.xpath('//div[@class="location_fullwidth_header_content"]/p/text()')
            )
            .strip()
            .lower()
        ):
            continue
        location_name = soup.find("title").text.strip()

        phone = "".join(sel.xpath('//div[@class="location-phone"]//text()')).strip()

        street_address = "".join(
            sel.xpath('//div[@class="street-address"]//text()')
        ).strip()
        city_state_zip = "".join(
            sel.xpath('//div[@class="city-state-zip"]//text()')
        ).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip_postal = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"
        try:
            store_number = re.search(
                r"\?store_id=(\d+)",
                soup.find("a", {"href": re.compile(r"\?store_id=\d+")})["href"],
            ).group(1)
        except:
            store_number = MISSING
        hours_of_operation = parse_hours(soup.find("div", {"class": "location-hours"}))
        latitude, longitude = get_latlong(soup)
        location_type = MISSING
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
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
