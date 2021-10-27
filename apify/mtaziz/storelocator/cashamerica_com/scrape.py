from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import pgeocode
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("cashamerica_com")
MISSING = SgRecord.MISSING

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


def fetch_data():
    with SgRequests() as session:
        url_store = "http://find.cashamerica.us/api/stores?p="
        url_key = "http://find.cashamerica.us/js/controllers/StoreMapController.js"
        logger.info(f"Extract key from: {url_key}")
        r = session.get(url_key, headers=headers)
        key = r.text.split("&key=")[1].split('");')[0]
        if key:
            logger.info(f"Key Found:{key}")
        else:
            logger.info(f"Unable to find the Key, please check the {url_key}")
        start = 1
        total_page_number = 2750  # As of now the last item returned by the page number 2711 while returning 1 item at a time
        items_num_per_page = 1
        total = 0
        for page in range(start, total_page_number):
            url_data = f"{url_store}{str(page)}&s={items_num_per_page}&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key={str(key)}"
            try:
                data = session.get(url_data, headers=headers).json()
                if "message" in data:
                    continue
            except Exception as e:
                logger.info(f"error loading the data:{e}")
                continue

            logger.info(f"[ Pulling the data from] {url_data}")
            found = 0
            for i in range(len(data)):
                store_data = data[i]

                # Locator Domain
                locator_domain = "cashamerica.com"

                # Page URL
                page_url = "<INACCESSIBLE>"

                # Location Name
                location_name = store_data["brand"] if store_data["brand"] else MISSING

                # Street Address
                street_address = ""
                if store_data["address"]["address2"] is not None:
                    street_address = (
                        store_data["address"]["address1"]
                        + store_data["address"]["address2"]
                    )
                else:
                    street_address = store_data["address"]["address1"]

                # City
                city = (
                    store_data["address"]["city"]
                    if store_data["address"]["city"]
                    else MISSING
                )

                # State
                state = ""
                if store_data["address"]["state"] in [
                    "AL",
                    "AK",
                    "AZ",
                    "AR",
                    "CA",
                    "CO",
                    "CT",
                    "DC",
                    "DE",
                    "FL",
                    "GA",
                    "HI",
                    "ID",
                    "IL",
                    "IN",
                    "IA",
                    "KS",
                    "KY",
                    "LA",
                    "ME",
                    "MD",
                    "MA",
                    "MI",
                    "MN",
                    "MS",
                    "MO",
                    "MT",
                    "NE",
                    "NV",
                    "NH",
                    "NJ",
                    "NM",
                    "NY",
                    "NC",
                    "ND",
                    "OH",
                    "OK",
                    "OR",
                    "PA",
                    "RI",
                    "SC",
                    "SD",
                    "TN",
                    "TX",
                    "UT",
                    "VT",
                    "VA",
                    "WA",
                    "WV",
                    "WI",
                    "WY",
                ]:
                    state = store_data["address"]["state"]
                state = state if state else MISSING

                # Zip Code
                zipcode = store_data["address"]["zipCode"]
                nomi = pgeocode.Nominatim("us")
                if nomi.query_postal_code(str(zipcode))["country_code"] != "US":
                    continue
                if "00000" in store_data["address"]["zipCode"]:
                    zipcode = MISSING
                zipcode = zipcode if zipcode else MISSING

                # Country Code
                country_code = "US"

                # Store Number
                store_number = (
                    store_data["storeNumber"] if store_data["storeNumber"] else MISSING
                )

                # Phone
                phone = (
                    "("
                    + store_data["phone"][0:3]
                    + ") "
                    + store_data["phone"][3:6]
                    + "-"
                    + store_data["phone"][6:10]
                )
                if "() -" in phone:
                    phone = MISSING
                phone = phone if phone else MISSING

                # Location Type
                location_type = ""
                if store_data["brand"]:
                    location_type = (
                        store_data["brand"]
                        .replace("0", "")
                        .replace("1", "")
                        .replace("2", "")
                        .replace("3", "")
                        .replace("4", "")
                        .replace("5", "")
                        .replace("6", "")
                        .replace("7", "")
                        .replace("8", "")
                        .replace("9", "")
                        .strip()
                    )
                else:
                    location_type = MISSING

                # Latitude
                latitude = store_data["latitude"] if store_data["latitude"] else MISSING

                # Longitude
                longitude = (
                    store_data["longitude"] if store_data["longitude"] else MISSING
                )

                # Hours of Operation
                hours_request = session.get(
                    "http://find.cashamerica.us/api/stores/"
                    + str(store_data["storeNumber"])
                    + "?key="
                    + key,
                    headers=headers,
                )
                hours_details = hours_request.json()["weeklyHours"]
                hours = ""
                for k in range(len(hours_details)):
                    if hours_details[k]["openTime"] != "Closed":
                        hours = (
                            hours
                            + " "
                            + hours_details[k]["weekDay"]
                            + " "
                            + hours_details[k]["openTime"]
                            + " "
                            + hours_details[k]["closeTime"]
                            + " "
                        )
                hours_of_operation = hours.strip() if hours != "" else MISSING

                # Raw Address
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
                found += 1
            total += found
            logger.info(f"Total Store Count: {total}")
        logger.info(f"Scraping Finished | Total Store Count: {total}")


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
