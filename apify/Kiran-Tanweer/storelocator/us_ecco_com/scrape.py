from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "us_ecco_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like GeneratorExitcko) Chrome/89.0.4389.114 Safari/537.36",
}


DOMAIN = "https://us.ecco.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://us.ecco.com/store-locator"
        stores_req = session.get(url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        scripts = soup.findAll("script")[19]
        scripts = str(scripts)
        locations = scripts.split('},{"storeID"')
        for loc in locations:
            loc = loc + "}"
            store = loc.split('"isECCOStore":')[1].split("}")[0]
            if store == "true":
                storeid = loc.split('","name"')[0]
                storeid = storeid.lstrip(':"').strip()
                title = loc.split('"name":"')[1].split('","')[0].strip()
                log.info(title)
                street = loc.split('"address1":"')[1].split('","')[0].strip()
                address = loc.split('"address":"')[1].split('","')[0].strip()
                pcode = address.split(",")[-1].strip()
                city = loc.split('"city":"')[1].split('","')[0].strip()
                state = loc.split('"stateCode":"')[1].split('","')[0].strip()
                country = loc.split('"countryCode":"')[1].split('","')[0].strip()
                phone = loc.split('"phone":"')[1].split('","')[0].strip()
                phone = phone.lstrip("+")
                lat = loc.split('"latitude":')[1].split(',"')[0]
                lng = loc.split('"longitude":')[1].split(',"')[0]
                if lat == "null":
                    lat = MISSING
                if lng == "null":
                    lng = MISSING
                hours = loc.split('"storeHours":')[1].split('],"')[0]
                hours = hours.split("},{")
                hoo = ""
                for hr in hours:
                    day = hr.split('"label":"')[1].split('","')[0]
                    hour = hr.split('"data":"')[1].split('"')[0]
                    h1 = day + " " + hour
                    hoo = h1 + " " + hoo
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=title,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=pcode,
                    country_code=country,
                    store_number=storeid,
                    phone=phone,
                    location_type="ECCO Store",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
