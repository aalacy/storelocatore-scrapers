import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "snipesusa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.snipesusa.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://stores.snipesusa.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.findAll(
            "div", {"class": "col-md-3 col-sm-6 col-xs-6 col-store-info store-info"}
        )
        for state in state_list:
            state = state.find("a")
            page_url = state["href"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            city_list = soup.findAll(
                "div", {"class": "col-md-3 col-sm-6 col-xs-6 col-store-info store-info"}
            )
            for city in city_list:
                city = city.find("a")
                log.info("Fetching " + city.text + " Locations...")
                page_url = city["href"]
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.findAll(
                    "div", {"class": "col-md-3 col-sm-6 col-xs-6 col-store-info"}
                )
                for loc in loclist:
                    loc = loc.find("a")
                    page_url = loc["href"]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = r.text.split('<script type="application/ld+json">')[
                        -1
                    ].split("</script>")[0]
                    temp = json.loads(temp)
                    store_number = temp["@id"]
                    location_name = temp["name"]
                    latitude = temp["geo"]["latitude"]
                    longitude = temp["geo"]["longitude"]
                    phone = temp["telephone"]
                    address = temp["address"]
                    street_address = address["streetAddress"]
                    city = address["addressLocality"]
                    state = address["addressRegion"]
                    zip_postal = address["postalCode"]
                    country_code = address["addressCountry"]
                    hour_list = temp["openingHoursSpecification"]
                    hours_of_operation = ""
                    for hour in hour_list:
                        hours_of_operation = (
                            hours_of_operation
                            + " "
                            + str(hour["dayOfWeek"])
                            .replace("[", "")
                            .replace("]", "")
                            .replace("'", "")
                            + " "
                            + hour["opens"]
                            + " - "
                            + hour["closes"]
                        )
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
                        hours_of_operation=hours_of_operation.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
