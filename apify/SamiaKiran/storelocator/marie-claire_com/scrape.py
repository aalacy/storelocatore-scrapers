import json
import unicodedata
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "marie-claire_com"
log = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "https://marie-claire.com/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        linklist = []
        url = "https://www.marie-claire.com/fr/boutiques"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "store-list"}).findAll(
            "div", {"class": "store-item"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            if page_url in linklist:
                continue
            linklist.append(page_url)
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            temp = r.text.split('<script type="application/ld+json">')[3].split(
                "</script>"
            )[0]
            temp = json.loads(temp, strict=False)
            hour_list = temp["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["dayOfWeek"].rsplit("/")[-1]
                    + " "
                    + hour["opens"]
                    + " - "
                    + hour["closes"]
                )
            address = temp["address"]

            street_address = address["streetAddress"]
            street_address = strip_accents(street_address)

            city = address["addressLocality"]
            city = strip_accents(city)

            state = address["addressRegion"]
            state = strip_accents(state)

            zip_postal = address["postalCode"]
            zip_postal = strip_accents(zip_postal)

            country_code = "CA"
            phone = temp["telephone"]
            phone = phone.replace("\t", " ")
            coords = temp["geo"]
            latitude = coords["latitude"]
            longitude = coords["longitude"]
            location_name = temp["name"]
            location_name = (
                unicodedata.normalize("NFD", location_name)
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            soup = BeautifulSoup(r.text, "html.parser")
            store_number = (
                soup.find("h1", {"class": "page-title"})
                .text.rsplit("-")[-1]
                .replace("\t", "")
                .strip()
            )
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
