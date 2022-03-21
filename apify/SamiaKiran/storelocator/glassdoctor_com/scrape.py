import re
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
website = "glassdoctor_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://glassdoctor.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text.strip())


def fetch_data():
    if True:
        url = "https://glassdoctor.com/locations-sitemap"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "view-content"}).findAll(
            "div", {"class": "field-content"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if loc.find("a").text == "Michigan" or "portland" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "Opening Soon!" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text.replace("\n", "")
            try:
                raw_address = (
                    soup.find("div", {"itemprop": "address"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace(",", " ")
                )
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
            except:
                try:
                    street_address = soup.find(
                        "span", {"itemprop": "streetAddress"}
                    ).text
                    city = soup.find("span", {"itemprop": "addressLocality"}).text
                    state = soup.find("span", {"itemprop": "addressRegion"}).text
                    zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
                    raw_address = (
                        street_address + " " + city + " " + state + " " + zip_postal
                    )
                except:
                    continue
            try:
                street_address = strip_accents(street_address)
                zip_postal = strip_accents(zip_postal.replace(",", ""))
                city = strip_accents(city)
            except:
                pass
            try:
                phone = r.text.split('data.trackNumber = ["')[1].split('"')[0]
                if "999-999-9999" in phone:
                    phone = soup.find("span", {"class": "phone"}).text
            except:
                try:
                    phone = soup.find("span", {"class": "phone"}).text
                except:
                    phone = soup.find("a", {"class": "fnt_phn"}).text

            try:
                if re.search("[a-zA-Z]", zip_postal):
                    country_code = "CA"
                else:
                    country_code = "US"
            except:
                pass
            phone = phone.replace("Call", "")
            if not city:
                city = r.text.split('"city":"')[1].split('"')[0]
            store_number = r.text.split('"franchisee":"')[1].split('"')[0]
            latitude = MISSING
            longitude = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address,
                city=city,
                state=state.strip(),
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
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
