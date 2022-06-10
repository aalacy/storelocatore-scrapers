from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton


DOMAIN = "https://www.noodles.com/"
logger = SgLogSetup().get_logger(logger_name="noodles_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

session = SgRequests()
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://locations.noodles.com/"
    store_url_list = []
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("li", {"class": "c-directory-list-content-item"})
    for idx1, state_url in enumerate(state_list):
        logger.info(f"Fetching locations from State {state_url.text}")
        if state_url.find("span").text == "(1)":
            temp = "https://locations.noodles.com/" + state_url.find("a")["href"]
            store_url_list.append(temp)
            logger.info(temp)
            state.push_request(SerializableRequest(url=temp))
        else:
            state_url = "https://locations.noodles.com/" + state_url.find("a")["href"]
            r2 = session.get(state_url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            city_list = soup2.findAll("li", {"class": "c-directory-list-content-item"})
            if not city_list:
                city_list = soup2.findAll("div", {"class": "c-location-grid-item"})
                for city in city_list:
                    loc = "https://locations.noodles.com/" + city.find("a")[
                        "href"
                    ].replace("..", "")
                    store_url_list.append(loc)
                    logger.info(loc)
                    state.push_request(SerializableRequest(url=loc))
            else:
                for city in city_list:
                    if city.find("span").text == "(1)":
                        temp = "https://locations.noodles.com/" + city.find("a")["href"]
                        store_url_list.append(temp)
                        logger.info(temp)
                        state.push_request(SerializableRequest(url=temp))
                    else:
                        city_url = (
                            "https://locations.noodles.com/" + city.find("a")["href"]
                        )
                        r4 = session.get(city_url, headers=headers)
                        soup4 = BeautifulSoup(r4.text, "html.parser")
                        loclist = soup4.findAll(
                            "div", {"class": "c-location-grid-item"}
                        )
                        for loc in loclist:
                            loc = "https://locations.noodles.com/" + loc.find("a")[
                                "href"
                            ].replace("..", "")
                            store_url_list.append(loc)
                            logger.info(loc)
                            state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(session: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = session.get(next_r.url.replace(".com//", ".com/"), headers=headers)
        logger.info(f"Pulling the data from: {next_r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        page_url = next_r.url
        location_name = soup.find("span", {"class": "location-name-geo"}).text
        try:
            street_address = (
                soup.find("span", {"class": "c-address-street-1"}).text
                + " "
                + soup.find("span", {"class": "c-address-street-2"}).text
            )
        except:
            street_address = soup.find("span", {"class": "c-address-street-1"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("abbr", {"itemprop": "addressRegion"}).text
        zip_postal = soup.find("span", {"class": "c-address-postal-code"}).text
        country_code = soup.find("abbr", {"itemprop": "addressCountry"}).text
        try:
            phone = soup.find("span", {"itemprop": "telephone"}).text
        except Exception:
            phone = "<MISSING>"

        try:
            hours_of_operation = (
                soup.find("table", {"class": "c-location-hours-details"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Day of the Week Hours ", "")
            )
        except Exception:
            hours_of_operation = "<MISSING>"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
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
            hours_of_operation=hours_of_operation,
        )


def scrape():
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        with SgRequests() as session:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(session, state)
            )
            for rec in fetch_records(session, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
