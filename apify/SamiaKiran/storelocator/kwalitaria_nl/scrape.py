import json
import html
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "kwalitaria_nl"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://kwalitaria.nl"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://kwalitaria.nl/api/locations"
        loclist = session.get(url, headers=headers).json()["locations"]
        for loc in loclist:
            page_url = loc["link"]
            location_name = html.unescape(strip_accents(loc["title"]))
            log.info(page_url)
            url = page_url + "/contact"
            r = session.get(url, headers=headers)
            schema = r.text.split('<script type="application/ld+json">')[1].split(
                "</script>", 1
            )[0]
            schema = schema.replace("\n", "")
            loc = json.loads(schema)
            location_name = loc["name"]
            address = loc["address"]
            phone = loc["telephone"]
            street_address = strip_accents(address["streetAddress"])
            city = strip_accents(address["addressLocality"])
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            latitude = loc["geo"]["latitude"]
            longitude = loc["geo"]["longitude"]
            hour_list = loc["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["dayOfWeek"].replace("http://schema.org/", "")
                    + " "
                    + hour["opens"]
                    + "-"
                    + hour["closes"]
                )
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
