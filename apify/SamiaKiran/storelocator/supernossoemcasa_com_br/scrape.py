import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "supernossoemcasa_com_br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
url = "https://www.supernossoemcasa.com.br/api/dataentities/SO/search?_fields=id,storeImage,address,city,complement,country,latitude,longitude,name,moreInfo,neighborhood,number,openingHour,phone,postalCode,state,name&_limit=1000"

headers = {
    "authority": "www.supernossoemcasa.com.br",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/vnd.vtex.ds.v10+json",
    "rest-range": "resources=0-1000",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.supernossoemcasa.com.br/lojas",
    "accept-language": "en-US,en;q=0.9",
}

DOMAIN = "https://supernossoemcasa.com.br/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = strip_accents(loc["name"].replace("||", ""))
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            street_address = strip_accents(loc["address"])
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postalCode"]
            country_code = loc["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = (
                strip_accents(loc["openingHour"])
                .replace("<br>", " ")
                .replace("</br>", " ")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.supernossoemcasa.com.br/lojas",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
