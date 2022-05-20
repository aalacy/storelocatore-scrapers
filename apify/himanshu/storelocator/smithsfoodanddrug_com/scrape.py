import json
import time
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "smithsfoodanddrug.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    }
    with SgRequests() as session:
        soup = BeautifulSoup(
            session.get(
                "https://www.smithsfoodanddrug.com/storelocator-sitemap.xml",
                headers=headers,
            ).text,
            "lxml",
        )
        for url in soup.find_all("loc")[:-1]:
            page_url = url.text
            log.info(page_url)
            location_resp = session.get(page_url, headers=headers).text
            location_soup = BeautifulSoup(location_resp, "lxml")
            store_sel = lxml.html.fromstring(location_resp)
            try:
                json_text = "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
                data = json.loads(json_text)
            except:
                try:
                    time.sleep(5)
                    log.info("Retrying ..")
                    session = SgRequests()
                    time.sleep(4)
                    location_resp = session.get(page_url, headers=headers).text
                    location_soup = BeautifulSoup(location_resp, "lxml")
                    store_sel = lxml.html.fromstring(location_resp)
                    json_text = "".join(
                        store_sel.xpath('//script[@type="application/ld+json"]/text()')
                    ).strip()
                    data = json.loads(json_text)
                except:
                    time.sleep(10)
                    log.info("Retrying ..")
                    session = SgRequests()
                    time.sleep(10)
                    location_resp = session.get(page_url, headers=headers).text
                    location_soup = BeautifulSoup(location_resp, "lxml")
                    store_sel = lxml.html.fromstring(location_resp)
                    json_text = "".join(
                        store_sel.xpath('//script[@type="application/ld+json"]/text()')
                    ).strip()
                    data = json.loads(json_text)
            location_name = location_soup.find(
                "h1", {"data-qa": "storeDetailsHeader"}
            ).text.strip()

            street_address = ""
            city = ""
            state = ""
            zip = ""
            try:
                street_address = data["address"]["streetAddress"]
                city = data["address"]["addressLocality"]
                state = data["address"]["addressRegion"]
                zip = data["address"]["postalCode"]
            except:
                raw_address = (
                    location_soup.find(class_="StoreAddress-storeAddressGuts")
                    .get_text(" ")
                    .replace(",", "")
                    .replace("5448  West", "5448 West")
                    .replace(" .", ".")
                    .replace("..", ".")
                    .split("  ")
                )
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()
                zip = raw_address[3].split("Get")[0].strip()

            country_code = "US"
            store_number = page_url.split("/")[-1]
            phone = data["telephone"]
            location_type = "<MISSING>"
            latitude = data["geo"]["latitude"]
            longitude = data["geo"]["longitude"]
            hours = " ".join(data["openingHours"])
            locator_domain = website
            hours_of_operation = (
                hours.replace("Su-Sa", "Sun - Sat :")
                .replace("-00:00", " - Midnight")
                .replace("Su ", "Sun ")
                .replace("Mo-Fr", "Mon - Fri")
                .replace("Sa ", "Sat")
            )
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
