import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "yogasix_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://yogasix.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://members.yogasix.com/api/brands/yogasix/locations?open_status=external&geoip=111.119.187.48&offer_slug="
        loclist = session.get(url, headers=headers).json()["locations"]
        for loc in loclist:
            if loc["coming_soon"] is True:
                continue
            location_name = loc["name"]
            store_number = loc["clubready_id"]
            page_url = loc["site_url"]
            log.info(page_url)
            phone = loc["phone"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            zip_postal = loc["zip"]
            country_code = loc["country_code"]
            state = loc["state"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            if page_url is None:
                hours_of_operation = MISSING
                page_url = MISSING
            else:
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    hours_js = soup.find(
                        class_="location-info-map__icon fas fa-clock"
                    ).find_next("span")["data-hours"]
                    raw_hours = json.loads(hours_js)
                    hours_of_operation = ""
                    for day in raw_hours:
                        hours_of_operation = (
                            hours_of_operation
                            + " "
                            + day.title()
                            + " "
                            + str(raw_hours[day])
                            .replace("], [", " | ")
                            .replace("'", "")
                            .replace(", ", " - ")
                            .replace("[[", "")
                            .replace("]]", "")
                        ).strip()
                except:
                    hours_of_operation = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
