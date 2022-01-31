import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "billabong_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://billabong.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        url = "https://www.billabong.com/on/demandware.store/Sites-BB-US-Site/en_US/StoreLocator-StoreLookup?mapRadius=200000&filterBBStores=true&filterBBRetailers=true&latitude=37.75870132446288&longitude=-122.4811019897461"
        loclist = session.get(url, headers=headers).json()["stores"]
        page_url = "https://www.billabong.com/stores/"
        for loc in loclist:
            hour_list = loc["storeHours"]
            hours_of_operation = ""
            for hour in hour_list:
                len_None = sum(x is None for x in hour)
                if len_None == 4:
                    continue
                else:
                    time = hour[0] + " " + hour[1] + "-" + hour[4]
                    hours_of_operation = hours_of_operation + time + " "
            if not hours_of_operation:
                hours_of_operation = MISSING
            location_name = strip_accents(loc["name"])
            store_number = loc["ID"]
            log.info(location_name)
            phone = loc["phone"]
            raw_address = (
                loc["address"]
                + " "
                + loc["city"]
                + " "
                + loc["postalCode"]
                + " "
                + loc["country"]
            )
            raw_address = raw_address.replace("\n", " ")
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            state = pa.state
            state = state.strip() if state else MISSING
            city = loc["city"]
            zip_postal = loc["postalCode"]
            country_code = loc["country"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=MISSING,
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
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
