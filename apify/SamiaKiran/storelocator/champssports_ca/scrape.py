import unicodedata
from sglogging import sglog
from typing import Iterable
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton

website = "champssports_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://champssports.ca/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://stores.champssports.ca/"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    country_list = soup.findAll("a", {"class": "Directory-listLink"})
    for country in country_list:
        count = country["data-count"]
        count = int(count.replace(")", "").replace("(", ""))
        country_url = "https://stores.champssports.ca/" + country["href"]
        if count > 1:
            log.info(f"Fetching data from State {country.text}")
            r = session.get(country_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                linklist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
                    "a", {"class": "Directory-listLink"}
                )
                for link in linklist:
                    loc_link = link["href"].replace(
                        "..", "https://stores.champssports.ca"
                    )
                    count = link["data-count"]
                    count = int(count.replace(")", "").replace("(", ""))
                    if count > 1:
                        r = session.get(loc_link, headers=headers)
                        soup = BeautifulSoup(r.text, "html.parser")
                        loclist = soup.find(
                            "ul", {"class": "Directory-listTeasers Directory-row"}
                        ).findAll("li")
                        for loc in loclist:
                            loc_link = loc.find("a", {"data-ya-track": "businessname"})[
                                "href"
                            ].replace("../..", "https://stores.champssports.ca")
                            store_url_list.append(loc_link)
                            log.info(loc_link)
                            state.push_request(SerializableRequest(url=loc_link))
                    else:
                        store_url_list.append(loc_link)
                        log.info(loc_link)
                        state.push_request(SerializableRequest(url=loc_link))
            except:
                linklist = soup.find(
                    "ul", {"class": "Directory-listTeasers Directory-row"}
                ).findAll("li")
                for link in linklist:
                    loc_link = link.find("a")["href"].replace(
                        "../..", "https://stores.champssports.ca"
                    )
                    store_url_list.append(loc_link)
                    log.info(loc_link)
                    state.push_request(SerializableRequest(url=loc_link))
        else:
            store_url_list.append(country_url)
            log.info(country_url)
            state.push_request(SerializableRequest(url=country_url))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        store_number = r.text.split('"storeId": "')[1].split('"')[0]
        log.info(f"Pulling the data from: {next_r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        street_address = strip_accents(
            soup.find("span", {"class": "c-address-street-1"}).text
        )
        city = soup.find("span", {"class": "c-address-city"}).text
        try:
            state = strip_accents(soup.find("abbr", {"itemprop": "addressRegion"}).text)
        except:
            state = MISSING
        try:
            zip_postal = strip_accents(
                soup.find("span", {"itemprop": "postalCode"}).text
            )
        except:
            zip_postal = MISSING
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
        try:
            phone = soup.find("div", {"itemprop": "telephone"}).text
        except:
            phone = MISSING
        location_name = (
            soup.find("h1", {"class": "Hero-title"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        try:
            hours_of_operation = (
                soup.find("table", {"class": "c-hours-details"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Day of the Week Hours", "")
            )
        except:
            hours_of_operation = MISSING
        country_code = strip_accents(
            soup.find("abbr", {"itemprop": "addressCountry"}).text
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=next_r.url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
