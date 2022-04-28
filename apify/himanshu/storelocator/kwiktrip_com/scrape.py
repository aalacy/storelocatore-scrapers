from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
DOMAIN = "bargainbasementhomecenter.com"
LOCATION_URL = "https://www.kwiktrip.com/Maps-Downloads/Store-List"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def fetch_data():
    r = session.get(LOCATION_URL, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    hours_of_operation = MISSING
    loclist = soup.find("tbody", {"class": "row-hover"}).find_all("tr")
    for loc in loclist:
        store_number = list(loc.stripped_strings)[0]
        url = "https://www.kwiktrip.com/ktapi/location/store/information/" + str(
            store_number
        )
        log.info(url)
        temp = session.get(url, headers=headers).json()
        location_name = temp["name"]
        phone = temp["phone"] or MISSING
        if temp["open24Hours"] is True:
            hours_of_operation = "Open 24 hours a day"
        else:
            hour_list = temp["hours"]
            hoo = ""
            try:
                for hour in hour_list:
                    day = hour["dayOfWeek"]
                    time = hour["openTime"] + "-" + hour["closeTime"]
                    hoo += day + " " + time + ","
            except:
                hoo = MISSING
            hoo.strip().rstrip(",")
            hours_of_operation = hoo.strip().rstrip(",")
        address = temp["address"]
        try:
            street_address = address["address1"] + " " + address["address2"]
        except:
            street_address = address["address1"]
        city = address["city"]
        state = address["state"]
        zip_postal = address["zip"]
        country_code = "US"
        soup = BeautifulSoup(r.text, "lxml")
        latitude = (
            list(loc.stripped_strings)[7]
            .replace("-93.22204", "MISSING")
            .replace("Yes", "MISSING")
        )
        longitude = list(loc.stripped_strings)[8]
        if (
            "Yes" in latitude
            or "Yes" in longitude
            or "No" in latitude
            or "No" in longitude
        ):
            latitude = MISSING
            longitude = MISSING
        country_code = "US"
        if "1208 W 13TH ST" in street_address:
            latitude = "42.15902"
            longitude = "-92.03876"
        if "https://www.kwiktrip.com/locator/store?id=589" in url:
            latitude = "42.03466"
            longitude = "-91.54563"
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
