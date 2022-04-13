import json
from sglogging import sglog
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa


session = SgRequests()
DOMAIN = "sullivanssteakhouse.com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

LOCATION_URL = "https://sullivanssteakhouse.com/location-search/"
MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = f"{street_address} {data.street_address_2}"
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    if True:
        r = session.get(LOCATION_URL, headers=HEADERS)
        soup = bs(r.content, "lxml")
        linklist = soup.findAll("div", {"class": "results-options"})
        coord_list = r.text.split("var ld_locations = ")[1].split("</script>")[0]
        coord_list = json.loads(coord_list)
        for link in linklist:
            page_url = link.findAll("a")[-1]["href"]
            soup = pull_content(page_url)
            location_type = MISSING
            try:
                hours_of_operation = (
                    soup.find("div", {"class": "e9370-13 x-text"})
                    .findAll("p")[1]
                    .get_text(separator=" ", strip=True)
                )
            except:
                text = soup.find("div", {"class": "e9370-13 x-text"}).text
                if "temporarily closed" in text:
                    hours_of_operation = MISSING
                    location_type = "Temporarily Closed"
                elif "coming soon" in text.lower():
                    hours_of_operation = MISSING
                    location_type = "Coming Soon"
            if "HAPPY HOUR" in hours_of_operation:
                hours_of_operation = (
                    soup.find("div", {"class": "e9370-13 x-text"})
                    .find("p")
                    .get_text(separator=" ", strip=True)
                    .replace("OPEN FOR DINE-IN", "")
                    .strip()
                )
            temp = soup.find("div", {"class": "e9370-10 x-text"}).findAll("p")
            phone = temp[1].find("a").text
            raw_address = (
                temp[0]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Get Directions", "")
                .strip()
                .rstrip(",")
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            city = city.replace("Lower Lobby,", "").strip()
            country_code = "US"
            location_name = soup.find("h1").text.replace("\n", "")
            for coord in coord_list:
                if location_name == coord["post_title"]:
                    store_number = coord["ID"]
                    latitude = coord["address"]["lat"]
                    longitude = coord["address"]["lng"]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
