import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "tanguay_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.tanguay.ca/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.tanguay.ca/fr/trouvez-un-magasin/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store_hlt_td"})
        for loc in loclist:
            location_name = loc.find("h3").text.replace("\n", "").strip()
            if "distribution" in location_name:
                continue
            log.info(location_name)
            temp = loc.findAll("div", {"class": "padding-store"})
            coords = temp[1].findAll("input", {"type": "hidden"})
            latitude = coords[0]["value"]
            longitude = coords[1]["value"]
            address = (
                temp[1]
                .text.replace("Adresse :", "")
                .replace("\n", "")
                .strip()
                .split(",")
            )
            if len(address) < 4:
                street_address = address[0].replace("Québec", "")
                city = "Québec"
                state = address[1]
                zip_postal = address[2]
            else:
                street_address = address[0]
                city = address[1]
                state = address[2]
                zip_postal = address[3]
                phone = temp[2].find("a").text
            country_code = "CA"
            hour_list = loc.find("table").findAll("tr")
            hours_of_operation = ""
            for hour in hour_list:
                day = hour.find("th").text.replace("\n", "").strip()
                time = hour.find("td").text.replace("\n", "").strip()
                hours_of_operation = hours_of_operation + " " + day + " " + time
            hours_of_operation = (
                hours_of_operation.replace("Lundi :", "Monday :")
                .replace("Mardi :", "Tuesday :")
                .replace("Mercredi :", "Wednesday :")
                .replace("Jeudi :", "Thursday :")
                .replace("Vendredi :", "Friday :")
                .replace("Samedi :", "Saturday :")
                .replace("Dimanche :", "Sunday :")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
