import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rodiziogrill_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.rodiziogrill.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.rodiziogrill.com/locations.aspx"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "locationsList"}).findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if "COMING SOON" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            temp = json.loads(
                r.text.split('<script type="application/ld+json">')[1].split(
                    "</script>"
                )[0]
            )
            coords = r.text.split("var json = [")[1].split("},")[0]
            latitude = coords.split("'lat': ")[1].split(",")[0]
            longitude = coords.split("'lng': ")[1].split(",")[0]
            try:
                street_address = temp["address"]["streetAddress"]
                city = temp["address"]["addressLocality"]
                state = temp["address"]["addressRegion"]
                zip_postal = temp["address"]["postalCode"]
                location_name = temp["name"]
            except:
                address = coords.split("<span>")[1].split("</span>")[0].split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                zip_postal = address[1]
                location_name = coords.split("'title': '")[1].split("',")[0]
            try:
                phone = temp["telephone"]
            except:
                phone = soup.select_one("a[href*=tel]").text
            hours_of_operation = r.text.split(
                '<div class="col-md-3 col-md-offset-0 Column2'
            )[1].split('<div class="col-md-3 col-md-offset-0 Column3')[0]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            if "Temporarily Closed" in hours_of_operation.text:
                hours_of_operation = MISSING
                location_type = "Temporarily Closed"
            else:
                location_type = MISSING
                hours_of_operation = hours_of_operation.get_text(
                    separator="|", strip=True
                ).split("|")[:-1]
                hours_of_operation = " ".join(x for x in hours_of_operation)
                hours_of_operation = (
                    hours_of_operation.split("\n")[1]
                    .replace("Hours", "")
                    .replace('">', "")
                    .replace("Dine-in open!", "")
                )
                if "**Holiday hours" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("**Holiday hours")[0]
                elif "*Dinner Pricing All Day" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split(
                        "*Dinner Pricing All Day"
                    )[0]
                if "*Takeout offered daily" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split(
                        "*Takeout offered daily"
                    )[0]
            country_code = "US"
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
