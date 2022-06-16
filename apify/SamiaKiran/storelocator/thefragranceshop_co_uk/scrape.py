from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thefragranceshop.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.thefragranceshop.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.thefragranceshop.co.uk/store-finder/listing"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "tfs-az-store-list-wrapper"}).findAll("a")
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code == 200:
                if "We have over 200 stores across the UK" in r.text:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h1").text
                raw_address = (
                    soup.find("div", {"class": "tfs-sd-address"})
                    .get_text(separator="|", strip=True)
                    .split("|")[1:]
                )
                phone = raw_address[-1]
                raw_address = " ".join(raw_address[:-2])
                raw_address = raw_address.replace("\n", " ")
                hour_list = soup.findAll("div", {"class": "tfs-hours-info"})
                hours_of_operation = ""
                for hour in hour_list:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + hour.get_text(separator="|", strip=True).replace("|", " ")
                    )
                latitude = r.text.split('"latitude":"')[1].split('"')[0]
                longitude = r.text.split('"longitude":"')[1].split('"')[0]
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = location_name.split()[0]
                state = MISSING

                zip_postal = raw_address.split()
                zip_postal = zip_postal[-2] + " " + zip_postal[-1]
                zip_postal = (
                    zip_postal.replace("Road", "")
                    .replace("Street,", "")
                    .replace("Centre", "")
                )
                if "Mall Hammersmith" in zip_postal:
                    zip_postal = MISSING
                street_address = street_address.replace(zip_postal, "")

                country_code = "UK"
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
