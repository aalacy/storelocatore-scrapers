import re
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
        pattern = re.compile(r"\s\s+")
        url = "https://wahlburgers.com/all-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.select("a[href*=location-details]")
        for link in linklist:
            page_url = "https://wahlburgers.com" + link["href"]
            if "Coming soon" in page_url:
                continue
            if "canada" in page_url:
                country_code = "Canada"
            elif "germany" in page_url:
                country_code = "Germany"
            else:
                country_code = "USA"
            r = session.get(page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("li", {"class": "single-location"})
            for loc in loclist:
                if "COMING SOON" in loc.text:
                    continue

                page_url = loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if "Coming soon" in r.text:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                raw_address = (
                    soup.find("div", {"class": "container grid location"})
                    .find("p")
                    .text
                )
                raw_address = (
                    re.sub(pattern, "\n", raw_address).replace("\n", " ").strip()
                )
                if "We are currently closed" in r.text:
                    location_type = "Temporarily Closed"
                else:
                    location_type = MISSING
                schema = r.text.split('<script type="application/ld+json">', 1)[
                    1
                ].split("</script>", 1)[0]
                location_name = schema.split('"name": "')[1].split('"')[0]
                try:
                    phone = schema.split('"telephone": "')[1].split('"')[0]
                except:
                    phone = MISSING
                street_address = schema.split('"streetAddress": "')[1].split('"')[0]
                city = schema.split('"addressLocality": "')[1].split('"')[0]
                zip_postal = schema.split('"postalCode": "')[1].split('"')[0]
                latitude = schema.split('"latitude":')[1].split(",")[0]
                longitude = (
                    schema.split('"longitude":')[1].split("}")[0].replace("\n", "")
                )

                hours_of_operation = (
                    schema.split('"openingHours":')[1]
                    .split("],")[0]
                    .replace("[", "")
                    .replace("\n", " ")
                    .replace("         ", " ")
                    .replace('"', "")
                    .replace(" ,", "")
                )
                pa = parse_address_intl(raw_address)
                state = pa.state
                state = state.strip() if state else MISSING
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
