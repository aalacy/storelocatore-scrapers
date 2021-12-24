import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "supermercadosmrspecial_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://supermercadosmrspecial.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://supermercadosmrspecial.com/serviciosalcliente/supermercados.asp"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "list_sup"}).findAll("li")
        for loc in loclist:
            temp = loc.find("div", {"class": "titulo"}).find("a")
            page_url = DOMAIN + temp["href"]
            location_name = strip_accents(temp.text)
            log.info(location_name)
            temp = loc.findAll("div")
            if "Horario" in temp[2].text:
                hours_of_operation = (
                    temp[2]
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                    .replace("Horario:", "")
                    .split("\r\n")
                )
                if "Cafetería" in hours_of_operation[1]:
                    del hours_of_operation[1]
                if "Cafetería" in hours_of_operation[-1]:
                    del hours_of_operation[-1]
                hours_of_operation = " ".join(
                    hour.strip() for hour in hours_of_operation
                )
                address = temp[3]
                phone = temp[4]
                coords = temp[5]
            else:
                hours_of_operation = MISSING
                address = temp[2]
                phone = temp[3]
                coords = temp[4]
            address = address.get_text(separator="|", strip=True).split("|")[1:]
            if "Email:" in address[-2]:
                address = address[:-2]
            if len(address) > 2:
                street_address = address[0] + " " + address[1]
                address = address[2].split(",")
            else:
                street_address = address[0]
                address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            phone = phone.get_text(separator="|", strip=True).split("|")[1]
            if "/" in phone:
                phone = phone.split("/")[0]
            latitude, longitude = (
                coords.find("a")["href"].split("q=")[1].split("&key")[0].split("%2C")
            )
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
