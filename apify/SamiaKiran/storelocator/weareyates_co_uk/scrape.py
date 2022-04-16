import re
from datetime import datetime
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from tenacity import retry, stop_after_attempt
import tenacity
import random
import time


session = SgRequests()
website = "www.greatukpubs_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.greatukpubs.co.uk/"
MISSING = SgRecord.MISSING


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            log.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://www.greatukpubs.co.uk/find-a-pub"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.findAll("div", {"class": "accordion-item"})
        for temp_state in state_list:
            loclist = temp_state.findAll("a", {"class": "inner-item"})
            for loc in loclist:
                location_name = loc.find("h5").text
                page_url = DOMAIN + loc["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                try:
                    soup = BeautifulSoup(r.text, "html.parser")
                except Exception as e:
                    try:
                        log.info(f"loclist Error: {e}")
                        response = get_response(temp_state, page_url)
                        soup = BeautifulSoup(response.text, "html.parser")
                    except:
                        continue
                today = datetime.today().strftime("%A")
                raw_address = (
                    soup.find("div", {"class": "address"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                raw_address = re.sub(pattern, "\n", raw_address).replace("\n", " ")
                phone = soup.select_one("a[href*=tel]").text
                hours_of_operation = (
                    soup.find("div", {"class": "opening-times"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Today", today)
                )
                latitude = r.text.split("lat: ")[1].split("}")[0]
                longitude = r.text.split("lng: ")[1].split(",")[0].replace("E", "")
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = "UK"
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
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
