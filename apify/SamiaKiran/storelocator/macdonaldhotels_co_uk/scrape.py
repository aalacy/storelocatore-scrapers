import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "macdonaldhotels_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.macdonaldhotels.co.uk"
MISSING = SgRecord.MISSING


def get_address(soup):
    try:
        raw_address = (
            soup.find("div", {"class": "infoPanel__address"})
            .find("p")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
    except:
        raw_address = (
            soup.find("p", {"class": "hotel-contact"})
            .find("span")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
    pa = parse_address_intl(raw_address.replace("View On Map", ""))

    street_address = pa.street_address_1
    street_address = street_address if street_address else MISSING

    city = pa.city
    city = city.strip() if city else MISSING

    state = pa.state
    state = state.strip() if state else MISSING

    zip_postal = pa.postcode
    zip_postal = zip_postal.strip() if zip_postal else MISSING

    return street_address, city, state, zip_postal, raw_address


def get_phone(soup):
    try:
        phone = soup.find("div", {"class": "infoPanel__tel"}).find("a").text
    except:
        phone = (
            soup.find("p", {"class": "hotel-contact"}).findAll("span")[1].find("a").text
        )
    return phone


def get_hours(soup):
    try:
        hours_of_operation = soup.find("p", string=re.compile("Check")).text
    except:
        hours_of_operation = MISSING
    return hours_of_operation


def fetch_data():
    if True:
        url = "https://www.macdonaldhotels.co.uk/our-hotels"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "hotel-link"})
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            if "our-hotels" not in page_url:
                continue
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = MISSING
            latitude = MISSING
            longitude = MISSING
            country_code = "GB"
            temp_list = soup.findAll("div", {"class": "sliderContent"})
            if temp_list:
                for temp in temp_list:
                    page_url = DOMAIN + temp.find("a")["href"]
                    log.info(page_url)
                    r = session.get(page_url, headers=headers)
                    soup_1 = BeautifulSoup(r.text, "html.parser")
                    try:
                        (
                            street_address,
                            city,
                            state,
                            zip_postal,
                            raw_address,
                        ) = get_address(soup_1)
                    except:
                        continue
                    phone = get_phone(soup_1)
                    hours_of_operation = get_hours(soup_1)
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
                        raw_address=raw_address,
                    )

            else:
                log.info(page_url)
                street_address, city, state, zip_postal, raw_address = get_address(soup)
                phone = get_phone(soup)
                hours_of_operation = get_hours(soup)
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
