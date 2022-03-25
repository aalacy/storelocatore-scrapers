from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "biglots.com"
BASE_URL = "https://local.biglots.com/"
LOCATION_URL = "https://local.biglots.com/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def parse_hours(table):
    if not table:
        return "<MISSING>"
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_store():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    state_links = soup.select("ul.Directory-listLinks a.Directory-listLink")
    for state_link in state_links:
        parent_page = pull_content(BASE_URL + state_link["href"])
        city_links = parent_page.select("ul.Directory-listLinks a.Directory-listLink")
        for city_link in city_links:
            count = city_link["data-count"].replace(")", "").replace("(", "")
            if int(count) > 1:
                data = pull_content(BASE_URL + city_link["href"])
                links = data.find_all("a", {"data-ya-track": "visitpage"})
                for row in links:
                    data = {
                        "url": BASE_URL + row["href"].replace("..", ""),
                        "state": state_link["href"].upper(),
                        "city": city_link.text.strip(),
                    }
                    store_urls.append(data)
            else:
                data = {
                    "url": BASE_URL + city_link["href"].replace("..", ""),
                    "state": state_link["href"].upper(),
                    "city": city_link.text.strip(),
                }
                store_urls.append(data)
    log.info("Found {} Stores ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    stores = fetch_store()
    for store in stores:
        page_url = store["url"]
        soup = pull_content(page_url)
        location_name = (
            soup.find("span", {"class": "LocationName"})
            .get_text(strip=True, separator=" ")
            .strip()
        )
        addr1 = soup.find("span", {"class": "c-address-street-1"})
        addr2 = soup.find("span", {"class": "c-address-street-2"})
        if addr2:
            street_address = "{}, {}".format(addr1.text, addr2.text)
        else:
            street_address = addr1.text
        street_address = street_address.strip().rstrip(".").rstrip(",")
        city = store["city"]
        state = store["state"]
        zip_postal = soup.find("span", {"class": "c-address-postal-code"}).text
        country_code = soup.find("address", {"id": "address"})["data-country"]
        store_number = MISSING
        phone = soup.find("div", {"id": "phone-main"})
        if not phone:
            phone = MISSING
        else:
            phone = phone.text
        hours = soup.find_all("td", {"class": "c-hours-details-row-intervals"})
        location_type = MISSING
        if all(value.text == "Closed" for value in hours):
            location_type = "TEMP_CLOSED"
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "c-hours-details"})
        )
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
