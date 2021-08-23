import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "partycity_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.partycity.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://stores.partycity.com/us/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("div", {"class": "tlsmap_list"}).findAll(
            "a", {"class": "gaq-link"}
        )
        for state in state_list:
            state_url = state["href"]
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            city_list = soup.find("div", {"class": "tlsmap_list"}).findAll(
                "a", {"class": "gaq-link"}
            )
            for city in city_list:
                city_url = city["href"]
                r = session.get(city_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.findAll("div", {"class": "map-list-item"})
                for loc in loclist:
                    page_url = loc.find("a")["href"]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    try:
                        if (
                            soup.find(
                                "div", {"class": "hours-status mb-15 is-closed"}
                            ).text
                            == "Opening Soon"
                        ):
                            continue
                    except:
                        pass
                    country_code = "US"
                    info = soup.find("script", {"type": "application/ld+json"}).text
                    loc = json.loads(info)[0]
                    address = loc["address"]
                    street_address = address["streetAddress"]
                    city = address["addressLocality"]
                    state = address["addressRegion"]
                    zip_postal = address["postalCode"]
                    phone = address["telephone"]
                    coords = loc["geo"]
                    latitude = coords["latitude"]
                    longitude = coords["longitude"]
                    hours_of_operation = loc["openingHours"]
                    location_name = loc["mainEntityOfPage"]["headline"]
                    try:
                        store_number = page_url.split("pc")[-1].split(".")[0]
                    except:
                        store_number = MISSING
                    location_type = MISSING
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
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
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
