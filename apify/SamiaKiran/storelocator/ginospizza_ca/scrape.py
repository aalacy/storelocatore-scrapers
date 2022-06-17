import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ginospizza.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.ginospizza.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.ginospizza.ca/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.find("select").findAll("option")[1:]
        for city_url in city_list:
            city = city_url.text
            log.info(f"Fetching Location from {city}")
            city_url = "https://www.ginospizza.ca/locations/" + city_url["value"]
            r = session.get(city_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"title": "Store Details"})
            for loc in loclist:
                page_url = loc["href"]
                page_url = loc["href"].strip().split("/")
                page_url = DOMAIN + "/".join(page_url[1:-2])
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h1").text
                latitude = r.text.split('"lat\\":\\"')[1].split("\\")[0]
                longitude = r.text.split('"long\\":\\"')[1].split("\\")[0]
                store_number = soup.find("h2").text.split("#")[1]
                address = (
                    soup.findAll("div", {"class": "flexrow__gutter"})[2]
                    .get_text(separator="|", strip=True)
                    .split("|")[:-1]
                )
                phone = address[-1]
                raw_address = html.unescape(" ".join(address[:-2]))
                address = raw_address.split(",")
                if len(address) > 4:
                    street_address = address[0] + " " + address[1]
                else:
                    street_address = address[0]
                zip_postal = address[-1]
                state = MISSING
                street_address = street_address.replace(city, "")
                hours_of_operation = (
                    soup.find("dl", {"class": "list--description gutter--top"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                country_code = "CA"
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
