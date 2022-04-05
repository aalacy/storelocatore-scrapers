import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "sparkasse_at"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.sparkasse.at"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://api.sparkasse.at/haystack/rest/branches?type=branch&excludeOmv=true&countryCode=AT&language=DE&userLatitude=47.58138779999999&userLongitude=14.2266276&longitude=14.2266276&latitude=47.58138779999999&excludeInstituteNumbers=2%2C188"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:

            address = loc["address"]
            street_address = strip_accents(address["street"])
            city = strip_accents(address["city"])
            state = strip_accents(address["federalState"])
            zip_postal = address["zipCode"]
            country_code = address["countryCode"]
            latitude = loc["location"]["latitude"]
            longitude = loc["location"]["longitude"]
            store_number = loc["ouId"]
            page_url = (
                "https://www.sparkasse.at/erstebank/filialen-oeffungszeiten/filialsuche/filiale"
                + "/"
                + zip_postal
                + "-"
                + city.lower().replace(".", "").replace(" ", "-")
                + "/"
                + street_address.lower().replace(" ", "-")
                + "/"
                + store_number
            )
            location_name = strip_accents(loc["description"])
            try:
                phone = loc["phone"]
            except:
                phone = MISSING
            try:
                hour_list = loc["openingHours"]
                hours_of_operation = ""
                for hour in hour_list:
                    day = hour["day"]
                    time = hour["periods"][0]
                    time = time["open"] + "-" + time["close"]
                    hours_of_operation = hours_of_operation + " " + day + " " + time
            except:
                hours_of_operation = MISSING
            log.info(location_name)
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
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
