import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "cosy-wasch_de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://cosy-wasch.de"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.cosy-wasch.de/standorte/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "bt_bb_link"})
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = strip_accents(
                soup.find("h1").get_text(separator="|", strip=True).replace("|", "")
            )
            temp = soup.findAll("div", {"class": "bt_bb_text"})
            raw_address = strip_accents(
                temp[0].get_text(separator="|", strip=True).replace("|", " ")
            )
            hour_list = temp[1].get_text(separator="|", strip=True).split("|")
            hours_of_operation = ""
            for hour in hour_list:
                if hour == "–":
                    break
                hours_of_operation = hours_of_operation + " " + hour
            hours_of_operation = strip_accents(
                hours_of_operation.replace("Sommer (01.04. – 31.10.):", "")
            )
            phone = temp[2].get_text(separator="|", strip=True).replace("|", "")
            if "SB-WASC" in phone:
                phone = temp[3].get_text(separator="|", strip=True).replace("|", "")
            coords = soup.find("div", {"class": "bt_bb_google_maps_location"})
            latitude = coords["data-lat"]
            longitude = coords["data-lng"]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if street_address.isdigit():
                street_address = (
                    raw_address.replace(city, "")
                    .replace(zip_postal, "")
                    .replace("  ", " ")
                )
            country_code = "DE"
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
