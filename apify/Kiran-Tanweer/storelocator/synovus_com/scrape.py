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

website = "synovus_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.synovus.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://www.synovus.com/locations/usa/index.html"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("a", {"class": "Directory-listLink"})
    for state_url in state_list:
        log.info(f"Fetching Locations from: {state_url.text}")
        state_url = "https://www.synovus.com/locations/usa/" + state_url["href"]
        r = http.get(state_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.findAll("a", {"class": "Directory-listLink"})
        for city in city_list:
            city_url = "https://www.synovus.com/locations/usa/" + city["href"]
            count = city["data-count"]
            count = int(count.replace(")", "").replace("(", ""))
            if count > 1:
                r = session.get(city_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.findAll(
                    "a", {"class": "Teaser-titleLink Link--directory"}
                )
                for loc in loclist:
                    loc_link = "https://www.synovus.com/locations/usa" + loc[
                        "href"
                    ].replace("..", "")
                    store_url_list.append(loc_link)
                    log.info(loc_link)
                    state.push_request(SerializableRequest(url=loc_link))
            else:
                store_url_list.append(city_url)
                log.info(city_url)
                state.push_request(SerializableRequest(url=city_url))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        log.info(f"Pulling the data from: {next_r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            street_address = strip_accents(
                soup.find("span", {"class": "Address-line1"}).text
                + " "
                + soup.find("span", {"class": "Address-line2"}).text
            )
        except:
            street_address = strip_accents(
                soup.find("span", {"class": "Address-line1"}).text
            )
        city = soup.find("span", {"class": "Address-city"}).text
        state = strip_accents(soup.find("abbr", {"itemprop": "addressRegion"}).text)
        zip_postal = strip_accents(soup.find("span", {"itemprop": "postalCode"}).text)
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
        phone = soup.find("a", {"data-ya-track": "phone"}).text
        location_name = soup.find("span", {"class": "LocationName-geo"}).text
        if "Office" in location_name:
            location_type = "Office " + location_name.split("Office")[1]
        elif "Branch" in location_name:
            location_type = "Branch " + location_name.split("Branch")[1]
        elif "Banking" in location_name:
            location_type = "Banking " + location_name.split("Banking")[1]
        elif "ATM" in location_name:
            location_type = "ATM"
        elif "Mortgage" in location_name:
            location_type = "Mortgage"
        elif "Private Wealth" in location_name:
            location_type = "Private Wealth Management"
        else:
            location_type = MISSING
        country_code = "US"
        hours_of_operation = (
            soup.find("table", {"class": "c-hours-details"})
            .find("tbody")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
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
            store_number=MISSING,
            phone=phone.strip(),
            location_type=location_type,
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
