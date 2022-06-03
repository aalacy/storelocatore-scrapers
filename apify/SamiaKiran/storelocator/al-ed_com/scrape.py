import json
import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "al-ed_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://al-ed.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://al-ed.com/storelocator"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_no = soup.find("a", {"class": "page"}).findAll("span")[-1].text
        page_no = int(page_no) + 1
        for x in range(1, page_no):
            url = "https://al-ed.com/amlocator/index/ajax/?p=" + str(x)
            r = session.get(url, headers=headers)
            loclist = r.text.split('jsonLocations: {"items":')[1].split("}]")[0] + "}]"
            loclist = json.loads(loclist)
            for loc in loclist:

                store_number = loc["id"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                temp = loc["popup_html"]
                loc = BeautifulSoup(temp, "html.parser")
                page_url = loc.find("a", {"class": "amlocator-link"})["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                address = soup.find(
                    "div", {"class": "amlocator-location-info"}
                ).findAll("div", {"class": "amlocator-block"})
                zip_postal = address[0].findAll("span")[-1].text
                state = address[2].findAll("span")[-1].text
                city = address[3].findAll("span")[-1].text
                street_address = address[4].findAll("span")[-1].text
                location_name = html.unescape(soup.find("h1").text)
                phone = soup.find("div", {"class": "amlocator-block -contact"}).findAll(
                    "div", {"class": "amlocator-block"}
                )
                phone = phone[1].find("a").text
                hour_list = soup.find(
                    "div", {"class": "amlocator-schedule-table"}
                ).findAll("div", {"class": "amlocator-row"})
                hours_of_operation = ""
                for hour in hour_list:
                    hour = hour.findAll("span")[:-2]
                    day = hour[0].text
                    time = hour[1].text
                    hours_of_operation = hours_of_operation + " " + day + " " + time

                country_code = "US"
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
