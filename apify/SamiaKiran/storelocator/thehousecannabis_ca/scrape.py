from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thehousecannabis_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://thehousecannabis.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://thehousecannabis.ca/stores/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "LocationTile__Container-sc-s93sol-1"})
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find(
                "h2", {"class": "LocationMap__Title-sc-1tudpe1-2"}
            ).text
            temp = soup.findAll(
                "div", {"class": "StoreFacts__Description-sc-19jbc8c-3"}
            )
            address = temp[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0].replace("in Chinatown", "")
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1] + " " + address[2]
            phone = temp[-1].get_text(separator="|", strip=True).split("|")[-1]
            hour_list = (
                soup.find("div", {"class": "LocationMap__Hours-sc-1tudpe1-4"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .lower()
                .strip()
                .replace("sunday", "sunday |")
            )
            hour_list = hour_list.split("|")
            day_list = hour_list[0].split()
            time_list = hour_list[1].replace(" - ", "-").split()
            hours_of_operation = ""
            for day, time in zip(day_list, time_list):
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + time.replace("-", " - ")
                )
            temp_zip = r.text.split('"postalCode":"')[1].split('"')[0]
            if temp_zip == zip_postal:
                latitude = r.text.split('"latitude":')[1].split(",")[0]
                longitude = (
                    r.text.split('"longitude":')[1].split(",")[0].replace("}", "")
                )
            else:
                latitude = MISSING
                longitude = MISSING
            country_code = "CA"
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
