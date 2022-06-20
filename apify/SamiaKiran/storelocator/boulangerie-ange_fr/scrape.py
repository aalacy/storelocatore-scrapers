import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests(verify_ssl=False)
website = "www.boulangerie-ange_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.boulangerie-ange.fr"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        loclist = r.text.split("var magasins_infos =")[1].split("}]")[0] + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = strip_accents(loc["nom_du_magasin"])
            store_number = loc["id"]
            phone = loc["telephone_du_magasin"]
            street_address = strip_accents(loc["adresse_du_magasin"])
            city = strip_accents(loc["ville_du_magasin"])
            state = MISSING
            zip_postal = str(loc["departement_du_magasin"]).split("-")[0]
            country_code = "FR"
            longitude, latitude = str(loc["coordonnees_gps_du_magasin"]).split(";")
            hours_of_operation = (
                BeautifulSoup(loc["horaires_full"], "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Dimanche – –", "")
            )
            page_url = DOMAIN + loc["url_page_boulangerie"]
            log.info(page_url)
            store_number = page_url.split("=")[1]
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
