import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gerbercollision_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.gerbercollision.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.gerbercollision.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.findAll("div", {"class": "col-xs-4"})
        for temp_state in state_list:
            url = DOMAIN + temp_state.find("a")["href"]
            r = session.get(url, headers=headers)
            log.info(f"Fetching locations from State {temp_state.find('a').text}")
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "row result"})
            for loc in loclist:
                page_url = DOMAIN + loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                try:
                    temp = json.loads(
                        r.text.split('<script type="application/ld+json">')[1].split(
                            "</script>"
                        )[0]
                    )
                except:
                    continue
                location_name = temp["name"]
                phone = temp["telephone"]
                address = temp["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
                latitude = temp["geo"]["latitude"]
                longitude = temp["geo"]["longitude"]
                hour_list = temp["openingHoursSpecification"]
                hours_of_operation = ""
                for hour in hour_list:
                    day = hour["dayOfWeek"].replace("https://schema.org/", "")
                    time = hour["opens"] + "-" + hour["closes"]
                    hours_of_operation = hours_of_operation + " " + day + " " + time
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
