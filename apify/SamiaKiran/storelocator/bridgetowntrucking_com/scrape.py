import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "bridgetowntrucking_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://bridgetowntrucking.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://bridgetowntrucking.com/contact/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<script type="application/ld+json">')[1].split(
            "</script>"
        )[0]
        loclist = json.loads(loclist)["subOrganization"]
        for loc in loclist:
            page_url = loc["url"]
            log.info(page_url)
            location_name = loc["name"]
            phone = loc["telephone"]
            address = loc["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            zip_postal = address["postalCode"]
            country_code = "US"
            geo = address["areaServed"]["geo"]["geoMidpoint"]
            latitude = geo["latitude"]
            longitude = geo["longitude"]
            hours_of_operation = (
                str(loc["openingHours"]).replace("['", "").replace("']", "")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
