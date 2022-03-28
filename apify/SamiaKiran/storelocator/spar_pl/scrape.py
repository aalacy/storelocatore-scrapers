import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "spar_pl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://spar.pl/"
MISSING = SgRecord.MISSING

payload = "action=shopsincity&lat=52.1799062&lng=20.9478161&distance=10000"
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
}


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://spar.pl/wp-admin/admin-ajax.php"
        loclist = session.post(url, headers=headers, data=payload).json()["locations"]
        for loc in loclist:
            temp = loc
            page_url = temp["permalink"]
            log.info(page_url)
            store_number = temp["id"]
            street_address = strip_accents(temp["adres"])
            city = strip_accents(temp["miasto"])
            state = MISSING
            zip_postal = temp["kod"]
            location_name = city
            country_code = "PL"
            latitude = temp["lat"]
            longitude = temp["lng"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            mon = temp["poniedzialek"]
            if not mon:
                mon = MISSING
            tue = temp["poniedzialek"]
            if not tue:
                tue = MISSING
            wed = temp["poniedzialek"]
            if not wed:
                wed = MISSING
            thu = temp["poniedzialek"]
            if not thu:
                thu = MISSING
            fri = temp["poniedzialek"]
            if not fri:
                fri = MISSING
            sat = temp["poniedzialek"]
            if not sat:
                sat = MISSING
            sun = temp["poniedzialek"]
            if not sun:
                sun = MISSING
            hours_of_operation = (
                " mon "
                + mon
                + " tue "
                + tue
                + " wed "
                + wed
                + " thu "
                + thu
                + " fri "
                + fri
                + " sat "
                + sat
                + " sun "
                + sun
            )
            if (
                hours_of_operation
                == "mon <MISSING> tue <MISSING> wed <MISSING> thu <MISSING> fri <MISSING> sat <MISSING> sun <MISSING>"
            ):
                hours_of_operation = MISSING
            phone = (
                soup.find("div", {"class": "flex-x white"})
                .get_text(separator="|", strip=True)
                .split("|")[-1]
            )
            if "sprawdź jak dojechać" in phone:
                phone = MISSING
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
