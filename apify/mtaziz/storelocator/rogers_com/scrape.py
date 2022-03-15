from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

DOMAIN = "https://www.rogers.com/"
logger = SgLogSetup().get_logger("rogers_com")
base_url = "https://www.rogers.com/stores/"
MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "application/json",
}

session = SgRequests()

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=25,
    max_search_results=50,
)


def fetch_data():
    maxZ = search.items_remaining()
    total = 0
    s = set()
    for zipcode in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()

        url_location = f"https://www.rogers.com/stores/index.html?q={zipcode}&l=en"
        logger.info(("Pulling zip Code %s... %s" % (zipcode, url_location)))
        data_json = session.get(url_location, headers=headers, timeout=120).json()
        js = data_json["response"]["entities"]
        total += len(js)
        for jj in js:
            j = jj.get("profile")
            a = j.get("address")
            location_name = j.get("name")
            if "Rogers" in location_name:
                locator_domain = DOMAIN
                logger.info(f"[Location Name: {location_name} ]")
                street_address = (
                    f"{a.get('line1')} {a.get('line2') or ''}".strip() or MISSING
                )
                logger.info(f"[Street Address: {street_address} ]")
                search.found_location_at(
                    j.get("yextDisplayCoordinate", {}).get("lat"),
                    j.get("yextDisplayCoordinate", {}).get("long"),
                )
                city = a.get("city") or MISSING
                state = a.get("region") or MISSING
                zip_postal = a.get("postalCode") or MISSING
                country_code = a.get("countryCode") or MISSING
                logger.info(
                    f"[City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}]"
                )

                # Store Number
                store_number = j.get("meta", {}).get("id") or MISSING
                logger.info(f"[Store Number: {store_number} ]")

                # Remove Duplicates
                if store_number in s:
                    continue
                s.add(store_number)

                # Page URL
                page_url = (
                    j.get("websiteUrl")
                    if j.get("websiteUrl")
                    else j.get("c_pagesURL") or MISSING
                )
                logger.info(f"[Rogers Page URL: {page_url} ]")

                # Phone Number
                phone = j.get("mainPhone", {}).get("display") or MISSING
                logger.info(f"[Phone: {phone}]")

                # Longitude
                latitude = j.get("yextDisplayCoordinate", {}).get("lat") or MISSING
                logger.info(f"[Latitude: {latitude}]")

                # Latitude
                longitude = j.get("yextDisplayCoordinate", {}).get("long") or MISSING
                logger.info(f"[Longitude: {longitude}]")

                # Location Type
                location_type = j.get("c_storeType") or MISSING
                logger.info(f"[Location Type: {location_type}]")

                # Hours of Operation
                hours = j.get("hours", {}).get("normalHours", [])
                _tmp = []
                for h in hours:
                    day = h.get("day")
                    if not h.get("isClosed"):
                        interval = h.get("intervals")
                        start = str(interval[0].get("start"))
                        if len(start) == 3:
                            start = f"0{start}"
                        end = str(interval[0].get("end"))
                        line = f"{day[:3].capitalize()}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
                    else:
                        line = f"{day[:3].capitalize()}: Closed"
                    _tmp.append(line)

                hours_of_operation = ";".join(_tmp) or MISSING
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "Closed"

                # Raw Address
                raw_address = (
                    f"{a.get('line1')} {a.get('line2') or ''} {a.get('line3') or ''}".strip()
                    or MISSING
                )
                logger.info(f"[Raw Address: {raw_address} ]")
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"found: {len(js)} | total: {total} | progress: {progress}")


def scrape():
    logger.info(" Scraping Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
