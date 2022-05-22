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

website = "versace_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://versace.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://boutiques.versace.com/us/en-us/index.html"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    country_list = soup.findAll("a", {"class": "Directory-listLink"})
    for country in country_list:
        count = country["data-count"]
        count = int(count.replace(")", "").replace("(", ""))
        country_url = country["href"].replace("../", "https://boutiques.versace.com/")
        if count > 1:
            log.info(f"Fetching data from Country {country.text}")
            r = session.get(country_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                linklist = soup.find("ul", {"class": "Directory-listLinks"}).findAll(
                    "a", {"class": "Directory-listLink"}
                )
                for link in linklist:
                    loc_link = link["href"].replace(
                        "../", "https://boutiques.versace.com/"
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
                            loc_link = loc.find("a", {"class": "Teaser-link"})[
                                "href"
                            ].replace("../../", "https://boutiques.versace.com/")
                            store_url_list.append(loc_link)
                            log.info(loc_link)
                            state.push_request(SerializableRequest(url=loc_link))
                    else:
                        store_url_list.append(loc_link)
                        log.info(loc_link)
                        state.push_request(SerializableRequest(url=loc_link))
            except:
                linklist = soup.findAll("a", {"class": "Teaser-link"})
                for link in linklist:
                    loc_link = link["href"].replace(
                        "../../", "https://boutiques.versace.com/"
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
        log.info(f"Pulling the data from: {next_r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            street = strip_accents(
                soup.find("span", {"class": "c-address-street-1"}).text
                + " "
                + soup.find("span", {"class": "c-address-street-2"}).text
            )
        except:
            street = strip_accents(
                soup.find("span", {"class": "c-address-street-1"}).text
            )
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
        try:
            country_code = strip_accents(
                soup.find("abbr", {"itemprop": "addressCountry"}).text
            )
        except:
            country_code = "Japan"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
        try:
            phone = soup.find("span", {"itemprop": "telephone"}).text
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
        raw_address = street + " " + city + " " + state + " " + zip_postal
        raw_address = raw_address.replace(MISSING, "")
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=next_r.url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
            raw_address=raw_address,
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
