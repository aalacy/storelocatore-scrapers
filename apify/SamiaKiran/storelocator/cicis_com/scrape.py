import json
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

website = "cicis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://cicis.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://cicis.com/locations/"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("li", {"class": "c-directory-list-content-item"})
    for temp_state in state_list:
        count = temp_state.find("span").text
        count = int(count.replace(")", "").replace("(", ""))
        state_url = "https://cicis.com/locations/" + temp_state.find("a")["href"]
        if count > 1:
            log.info(f"Fetching locations from State {temp_state.find('a').text}")
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            city_list = soup.findAll("li", {"class": "c-directory-list-content-item"})
            for city in city_list:
                count = temp_state.find("span").text
                count = int(count.replace(")", "").replace("(", ""))
                city_url = "https://cicis.com/locations/" + city.find("a")["href"]
                if count > 1:
                    r = session.get(city_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    loclist = soup.findAll("a", {"class": "location-title-link"})
                    for loc in loclist:
                        loc_link = "https://cicis.com/locations/" + loc["href"]
                        store_url_list.append(loc_link)
                        log.info(loc_link)
                        state.push_request(SerializableRequest(url=loc_link))
                else:
                    store_url_list.append(city_url)
                    log.info(city_url)
                    state.push_request(SerializableRequest(url=city_url))
        else:
            store_url_list.append(state_url)
            log.info(state_url)
            state.push_request(SerializableRequest(url=state_url))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        log.info(f"Pulling the data from: {next_r.url}")
        page_url = next_r.url
        soup = BeautifulSoup(r.text, "html.parser")
        if "Closed" in soup.find("h1").text:
            continue
        location_name = (
            soup.find("span", {"class": "c-location-title-row"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        street_address = soup.find("span", {"class": "c-address-street-1"}).text
        city = soup.find("span", {"class": "c-address-city"}).text.replace(",", "")
        state = soup.find("span", {"itemprop": "addressRegion"}).text
        zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
        country_code = "US"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
        phone = soup.find("span", {"itemprop": "telephone"}).text
        hour_list = soup.find("div", {"class": "c-location-hours-details-wrapper"})[
            "data-days"
        ]
        hour_list = json.loads(hour_list)
        hours_of_operation = ""
        for hour in hour_list:
            time = hour["intervals"][0]
            start = time["start"]
            end = time["end"]
            time = str(start) + "-" + str(end)
            hours_of_operation = hours_of_operation + " " + hour["day"] + " " + time
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
