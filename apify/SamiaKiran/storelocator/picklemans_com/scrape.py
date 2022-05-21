import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "picklemans_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.picklemans.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/1554/stores.js?callback=SMcallback2"
        r = session.get(url, headers=headers)
        loclist = json.loads(r.text.split("SMcallback2(")[1].split("}]})")[0] + "}]}")[
            "stores"
        ]
        for loc in loclist:
            if "COMING SOON" in loc["description"]:
                continue
            location_name = BeautifulSoup(loc["name"], "html.parser").text
            store_number = loc["id"]
            phone = loc["phone"]
            address = BeautifulSoup(loc["address"], "html.parser")
            page_url = address.find("a")["href"]
            if "picklemans" not in page_url:
                page_url = DOMAIN + address.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                day = soup.find("span", {"itemprop": "dayOfWeek"}).text
                opens = soup.find("span", {"itemprop": "opens"}).text
                closes = soup.find("span", {"itemprop": "closes"}).text
                hours_of_operation = day + " " + opens + "-" + closes
            except:
                try:
                    hours_of_operation = (
                        soup.findAll("bd1")[-1]
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .split("Hours:")[1]
                    )
                except:
                    hours_of_operation = (
                        soup.findAll("bd1")[0]
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        .split("Hours:")[1]
                    )
            hours_of_operation = re.sub(pattern, "\n", hours_of_operation)
            hours_of_operation = hours_of_operation.replace("\n", " ")
            street_address = soup.find("span", {"itemprop": "streetAddress"}).text
            city = soup.find("span", {"itemprop": "addressLocality"}).text
            try:
                state = soup.find("span", {"itemprop": "addressRegion"}).text.replace(
                    ",", ""
                )
            except:
                if "Kansas" in city:
                    state = "MO"
            zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            if "None" in hours_of_operation:
                hours_of_operation = MISSING
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
