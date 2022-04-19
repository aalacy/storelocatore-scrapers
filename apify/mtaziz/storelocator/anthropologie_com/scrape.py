from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger(logger_name="anthropologie_com")

locator_domain_url = "https://www.anthropologie.com"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

MISSING = SgRecord.MISSING


def get_hoo(hours):
    dates_map = {
        "1": "Sunday",
        "2": "Monday",
        "3": "Tuesday",
        "4": "Wednesday",
        "5": "Thursday",
        "6": "Friday",
        "7": "Saturday",
    }
    hoo = []
    for key, value in hours.items():
        v = dates_map[key] + " " + value["open"] + " - " + value["close"]
        hoo.append(v)
    hoo = "; ".join(hoo)
    if hoo:
        return hoo
    else:
        return MISSING


def fetch_data():
    with SgRequests() as session:
        url_api = "https://www.anthropologie.com/api/misl/v1/stores/search?brandId=54%7C04&distance=25&urbn_key=937e0cfc7d4749d6bb1ad0ac64fce4d5"
        data = session.get(url_api, headers=headers).json()
        for idx, d in enumerate(data["results"]):
            country_code = d["country"]
            locator_domain = locator_domain_url

            try:
                location_name = d["addresses"]["marketing"]["name"]
            except:
                location_name = d["storeName"]
            page_url = ""
            if "slug" in d:
                slug = d["slug"]
                if slug:
                    page_url = f"https://www.anthropologie.com/stores/{slug}"
                else:
                    page_url = MISSING
            else:
                page_url = MISSING
            street_address = d["addressLineOne"] if d["addressLineOne"] else MISSING
            city = d["city"] if d["city"] else MISSING
            state = d["state"] if d["state"] else MISSING
            zipcode = d["zip"] if d["zip"] else MISSING
            country_code = d["country"] if d["country"] else MISSING
            store_number = d["storeNumber"] if d["storeNumber"] else MISSING
            try:
                phone = d["addresses"]["marketing"]["phoneNumber"]
            except KeyError:
                phone = MISSING
            try:
                location_type = d["storeType"]
            except KeyError:
                location_type = MISSING
            try:
                latitude = d["loc"][1]
            except:
                latitude = MISSING
            try:
                longitude = d["loc"][0]
            except:
                longitude = MISSING
            hours_of_operation = get_hoo(d["hours"])
            if (
                page_url == "https://www.anthropologie.com/stores"
                and street_address == MISSING
            ):
                continue
            else:
                if page_url == "https://www.anthropologie.com/stores":
                    page_url = MISSING
            raw_address = MISSING
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
