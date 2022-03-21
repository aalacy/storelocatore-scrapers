import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "flannels_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://flannels.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        day_list = {
            0: "Mon",
            1: "Tue",
            2: "Wed",
            3: "Thu",
            4: "Fri",
            5: "Sat",
            6: "Sun",
        }
        url = "https://www.flannels.com/sitemap"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "stores"}).findAll("li")
        for loc in loclist:
            page_url = "https://www.flannels.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            try:
                loc = json.loads(r.text.split("var store =")[1].split("};")[0] + "}")
            except:
                continue
            location_name = loc["name"]
            store_number = loc["code"]
            phone = loc["telephone"]
            street_address = loc["address"]
            city = loc["town"]
            state = MISSING
            zip_postal = loc["postCode"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            country_code = loc["country"]
            hour_list = loc["openingTimes"]
            hours_of_operation = ""
            for hour in hour_list:
                day = day_list[hour["dayOfWeek"]]
                open_time = hour["openingTime"]
                close_time = hour["closingTime"]
                try:
                    time = open_time + " " + close_time
                except:
                    time = "Closed"
                hours_of_operation = hours_of_operation + " " + day + ": " + time
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
