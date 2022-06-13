from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "aadhaarretail_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": "PHPSESSID=26515e67845475c965ad22deddd60915",
}

headers2 = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=26515e67845475c965ad22deddd60915",
}

DOMAIN = "https://aadhaarretail.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "http://www.aadhaarretail.com/our-store"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        loc_block = soup.find("select", {"id": "state"}).findAll("option")
        for states in loc_block:
            state = states["value"]
            if state != "":
                url = "http://www.aadhaarretail.com/ajaxStore.php"
                payload = "stateId=" + state
                req = session.post(url, headers=headers2, data=payload)
                cities = BeautifulSoup(req.text, "html.parser")
                cities = cities.findAll("option")
                for city in cities:
                    city = city["value"]
                    if city != "":
                        url = "http://www.aadhaarretail.com/ajaxStore.php"
                        payload = "cityId=" + city
                        req = session.post(url, headers=headers2, data=payload)
                        stores = BeautifulSoup(req.text, "html.parser")
                        stores = stores.findAll("option")
                        for store in stores:
                            store = store["value"]
                            title = store
                            if store != "":
                                url = "http://www.aadhaarretail.com/ajaxStore.php"
                                payload = "storeId=" + store
                                req = session.post(url, headers=headers2, data=payload)
                                store = BeautifulSoup(req.text, "html.parser")
                                coords = store.find("iframe")["src"]
                                ptag = store.findAll("p")
                                address = ptag[0].text
                                city = city
                                state = state
                                pcode = ptag[3].text
                                phone = ptag[4].text
                                phone = phone.lstrip("Contact No. - ")
                                address = address.lstrip("Address - ")
                                pcode = pcode.lstrip("Zip Code - ")
                                coords = coords.split("q=")[1].split("&")[0]
                                lat, lng = coords.split(", ")
                                street = address.replace(",,", " ")
                                street = street.lstrip(",")

                                raw = street

                                yield SgRecord(
                                    locator_domain=DOMAIN,
                                    page_url="http://www.aadhaarretail.com/our-store",
                                    location_name=title,
                                    street_address=street.strip(),
                                    city=city.strip(),
                                    state=state.strip(),
                                    zip_postal=pcode,
                                    country_code="IN",
                                    store_number=MISSING,
                                    phone=phone,
                                    location_type=MISSING,
                                    latitude=lat,
                                    longitude=lng,
                                    hours_of_operation=MISSING,
                                    raw_address=raw,
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
