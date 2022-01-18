import json
from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton

DOMAIN = "https://www.meineke.com/"
logger = SgLogSetup().get_logger(logger_name="meineke_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://api.meineke.com/api/stores/states/"
    store_url_list = []
    http = SgRequests()
    state_list = http.get(url, headers=headers).json()["message"]
    for state_url in state_list:
        logger.info(f"Fetching from State: {state_url['stateName']}")
        state_url = (
            "https://api.meineke.com/api/stores/cities/?state="
            + state_url["stateAbbreviation"]
        )
        city_list = http.get(state_url, headers=headers).json()["message"]["cities"]
        for city_url in city_list:
            logger.info(f"Fetching from City : {city_url['cityName']}")
            city_url = "https://www.meineke.com/locations/?key=" + city_url["citySlug"]
            r = http.get(city_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "location-detail"})
            for loc in loclist:
                loc = loc.find("a")["href"]
                store_url_list.append(loc)
                logger.info(loc)
                state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        logger.info(f"Pulling the data from: {next_r.url}")
        page_url = next_r.url
        try:
            schema = r.text.split('<script type="application/ld+json">', 2)[1].split(
                "</script>", 1
            )[0]
            schema = schema.replace("\n", "")
            loc = json.loads(schema)
        except Exception as e:
            logger.info(f"Error: {e}")
            continue
        store_number = r.text.split('data-storeId="')[1].split('"')[0]
        location_name = loc["name"]
        phone = loc["telephone"]
        if phone == 0:
            phone = MISSING
        address = loc["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        country_code = address["addressCountry"]
        latitude = loc["geo"]["latitude"]
        longitude = loc["geo"]["longitude"]
        try:
            hour_list = loc["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                day = (
                    str(hour["dayOfWeek"])
                    .replace("', '", ", ")
                    .replace("['", "")
                    .replace("']", "")
                )
                time = hour["opens"] + "-" + hour["closes"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
        except:
            hours_of_operation = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
            hours_of_operation=hours_of_operation,
        )


def scrape():
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
