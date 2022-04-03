from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "strawberrycones_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.strawberrycones.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.strawberrycones.com/store/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        table_list = soup.find("div", {"class": "area_box_wrap"}).findAll("table")
        for table in table_list:
            city_list = table.findAll("a")
            for city_url in city_list:
                city_url = city_url["href"]
                r = session.get(city_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                loclist = soup.findAll("div", {"class": "region_detail"})
                for loc in loclist:
                    page_url = loc.find("a")["href"]
                    store_number = page_url.split("/")[-2]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    location_name = soup.find("h2").text
                    temp = soup.find("div", {"class": "store_detail"}).findAll("tr")
                    raw_address = (
                        temp[0].get_text(separator="|", strip=True).replace("|", " ")
                    )
                    # Parse the
                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street_address = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    zip_postal = zip_postal.strip() if zip_postal else MISSING

                    phone = temp[1].select_one("a[href*=tel]").text
                    hours_of_operation = temp[2].find("td").text
                    longitude, latitude = (
                        soup.select_one("iframe[src*=maps]")["src"]
                        .split("!2d", 1)[1]
                        .split("!2m", 1)[0]
                        .split("!3d")
                    )
                    country_code = "Japan"
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
                        location_type=MISSING,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
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
