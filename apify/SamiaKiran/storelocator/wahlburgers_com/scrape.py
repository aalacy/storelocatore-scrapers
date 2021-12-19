from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wahlburgers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}
DOMAIN = "https://wahlburgers.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://wahlburgers.com/all-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "cell medium-6"}).findAll("a")
        for link in linklist:
            page_url = "https://wahlburgers.com" + link["href"]
            log.info(page_url)
            if "Coming soon" in page_url:
                continue
            if "canada" in page_url:
                country_code = "Canada"
            elif "germany" in page_url:
                country_code = "Germany"
            else:
                country_code = "USA"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("div", {"class": "cell"}).findAll(
                "a", {"class": "fadey"}
            )
            for loc in loclist:
                try:
                    page_url = "https://wahlburgers.com" + loc["href"]
                    r = session.get(page_url, headers=headers)
                    if "Coming soon" in r.text:
                        continue
                    soup = BeautifulSoup(r.text, "html.parser")
                    temp = soup.find("div", {"class": "insideThing"}).findAll("div")
                    if "We are currently closed" in r.text:
                        location_type = "Temporarily Closed"
                    else:
                        location_type = "<MISSING>"
                except:
                    continue
                log.info(page_url)
                location_name = (
                    soup.find("div", {"class": "location whitepage"})
                    .find("h1")
                    .text.replace("@", "")
                    .replace("\n", "")
                    .split()
                )
                location_name = " ".join(x for x in location_name)
                if "General Manager:" in temp[-1].text:
                    del temp[-1]
                if len(temp) > 3:
                    temp = temp[1:]
                try:
                    phone = soup.select_one("a[href*=tel]").text.replace("Call", "")
                except:
                    phone = MISSING
                try:

                    hours_of_operation = (
                        temp[2].get_text(separator="|", strip=True).replace("|", " ")
                    ).replace("Opening hours:", "")
                    address = temp[1].get_text(separator="|", strip=True).split("|")[1:]
                except:
                    hours_of_operation = (
                        temp[1].get_text(separator="|", strip=True).replace("|", " ")
                    ).replace("Opening hours:", "")
                    address = temp[0].get_text(separator="|", strip=True).split("|")[1:]
                raw_address = " ".join(
                    x.replace("\n", "").replace("    ", " ") for x in address
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
                try:
                    longitude, latitude = (
                        soup.select_one("iframe[src*=maps]")["src"]
                        .split("!2d", 1)[1]
                        .split("!3m")[0]
                        .split("!3d")
                    )
                except:
                    latitude = MISSING
                    longitude = MISSING
                latitude = latitude.split("!2m")[0]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=location_type,
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
