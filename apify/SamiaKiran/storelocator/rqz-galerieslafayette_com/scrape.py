import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rqz-galerieslafayette_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


DOMAIN = "https://rqz-galerieslafayette.com/"
MISSING = SgRecord.MISSING


payload = "perpage=200&distance=4000000&maxitems=200"
headers = {
    "Connection": "keep-alive",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://stores.rqz-galerieslafayette.com",
}


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://stores.rqz-galerieslafayette.com/fr_FR/controller/rqz/liste-magasins/region/0/departement/0/code_insee_ville/0"
        r = session.post(url, headers=headers, data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("script")
        for loc in loclist[:-1]:
            try:
                schema = (loc.contents[0]).split("=", 1)[1].split(";", 1)[0]
                schema = schema.replace("\n", "")
                loc = json.loads(schema)
            except Exception as e:
                log.info(f"Error: {e}")
                continue
            page_url = loc["url"]
            log.info(page_url)
            location_name = strip_accents(loc["title"])
            store_number = loc["storeCode"]
            phone = loc["telephone"]
            try:
                street_address = loc["adresse1"] + " " + loc["address2"]
            except:
                street_address = loc["adresse1"]
            street_address = strip_accents(street_address)
            city = strip_accents(loc["ville"])
            state = strip_accents(loc["pays"])
            zip_postal = loc["codePostal"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            temp = loc["horairesSemaine"]
            su = temp["1"]
            mo = temp["2"]
            tu = temp["3"]
            we = temp["4"]
            th = temp["5"]
            fr = temp["6"]
            sa = temp["7"]
            hours_of_operation = (
                "Mon "
                + mo
                + " Tue "
                + tu
                + " Wed "
                + we
                + " Thu "
                + th
                + " Fri "
                + fr
                + " Sat "
                + sa
                + " Sun "
                + su.replace("Fermé", "Closed")
            )
            country_code = "FR"
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
