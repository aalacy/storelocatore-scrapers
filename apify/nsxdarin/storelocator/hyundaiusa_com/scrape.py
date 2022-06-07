from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_results=45,
)

session = SgRequests()
website = "hyundaiusa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


DOMAIN = "https://www.hyundaiusa.com"
MISSING = SgRecord.MISSING
headers = {
    "authority": "www.hyundaiusa.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hyundaiusa.com/us/en/dealer-locator",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    for code in search:
        url = (
            "https://www.hyundaiusa.com/var/hyundai/services/dealer/dealersByZip.json?brand=hyundai&model=all&lang=en_US&zip="
            + code
            + "&maxdealers=45"
        )
        try:
            loclist = session.get(url, headers=headers).json()["dealers"]
        except:
            continue
        for loc in loclist:
            page_url = loc["cobaltDealerURL"]
            location_name = loc["dealerNm"]
            store_number = loc["dealerCd"]
            phone = loc["phone"]
            try:
                street_address = loc["address1"] + " " + loc["address2"]
            except:
                street_address = loc["address1"]
            log.info(street_address)
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zipCd"]
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            search.found_location_at(latitude, longitude)
            phone = loc["phone"]
            hour_list = loc["operations"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["day"]
                time = hour["hour"]
                hours_of_operation = hours_of_operation + " " + day + " " + time

            if hours_of_operation == "":
                hour_list = loc["showroom"]
                hours_of_operation = ""
                for hour in hour_list:
                    day = hour["day"]
                    time = hour["hour"]
                    hours_of_operation = hours_of_operation + " " + day + " " + time

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
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
