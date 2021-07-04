import time
from concurrent.futures import ThreadPoolExecutor
from sgzip.static import static_zipcode_list, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sglogging import SgLogSetup

website = "aldi.us"

logger = SgLogSetup().get_logger(website)

max_workers = 24

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetchSingleZip(zip_code):
    locations_all = []
    logger.info(zip_code)
    url = (
        "https://www.aldi.us/stores/en-us/Search?SingleSlotGeo="
        + str(zip_code)
        + "&Mode=None"
    )
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    purl = "<MISSING>"
    typ = "Store"
    phone = "<MISSING>"
    result = []
    for line in r.iter_lines(decode_unicode=True):
        if '<li tabindex="' in line:
            try:
                store = line.split(";weeklyAdId&quot;:&quot;")[1].split("&")[0]
            except:
                store = "<MISSING>"
            try:
                lng = line.split("locX&quot;:&quot;")[1].split("&")[0]
                lat = line.split("locY&quot;:&quot;")[1].split("&")[0]
            except:
                lat = "<MISSING>"
                lng = "<MISSING>"
        if 'itemprop="name">' in line:
            hours = ""
            name = line.split('itemprop="name">')[1].split("<")[0]
        if '"streetAddress" class="resultItem-Street">' in line:
            add = line.split('"streetAddress" class="resultItem-Street">')[1].split(
                "<"
            )[0]
        if 'itemprop="telephone" href="tel:' in line:
            phone = line.split('itemprop="telephone" href="tel:')[1].split('"')[0]
        if 'class="resultItem-City" data-city="' in line:
            try:
                city = line.split('class="resultItem-City" data-city="')[1].split(",")[
                    0
                ]
                state = (
                    line.split('class="resultItem-City" data-city="')[1]
                    .split(",")[1]
                    .split('"')[0]
                    .strip()
                )
                zc = line.split('">')[1].split("<")[0].strip().rsplit(" ", 1)[1]
                country = "US"
            except:
                state = "<MISSING>"
        if '<td class="open">' in line:
            if hours == "":
                hours = line.split('<td class="open">')[1].split("<")[0] + ": "
            else:
                hours = (
                    hours
                    + "; "
                    + line.split('<td class="open">')[1].split("<")[0]
                    + ": "
                )
        if '<td class="open openingTime">' in line:
            hours = hours + line.split('<td class="open openingTime">')[1].split("<")[0]
        if '<div class="onlyMobile resultItem-Arrow">' in line:

            location_info = {
                "address": add,
                "city": city,
                "state": state,
                "lat": lat,
                "lng": lng,
            }

            if location_info not in locations_all:
                locations_all.append(location_info)
                if hours == "":
                    hours = "<MISSING>"
                if state != "<MISSING>":
                    result.append(
                        {
                            "locator_domain": website,
                            "page_url": purl,
                            "location_name": name,
                            "street_address": add,
                            "city": city,
                            "state": state,
                            "zip_postal": zc,
                            "country_code": country,
                            "store_number": store,
                            "phone": phone,
                            "location_type": typ,
                            "latitude": lat,
                            "longitude": lng,
                            "hours_of_operation": hours,
                        }
                    )

    return zip_code, result, None


def fetchData():
    zips = static_zipcode_list(radius=5, country_code=SearchableCountries.USA)
    logger.info(f"Total Zip Codes to scan: {len(zips)}")
    countZip = 0
    count = 0

    storeNumbers = []
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for zip_code, result, error in executor.map(fetchSingleZip, zips):
            if countZip % 100 == 0:
                logger.info(f"total zip code = {countZip} total stores = {count}")

            countZip = countZip + 1
            if error is not None:
                continue

            for details in result:
                raw_address = f"{details['street_address']}, {details['city']}, {details['state']} {details['zip_postal']}"
                if details["store_number"] in storeNumbers:
                    continue
                storeNumbers.append(details["store_number"])
                count = count + 1
                yield SgRecord(
                    locator_domain=details["locator_domain"],
                    store_number=details["store_number"],
                    page_url=details["page_url"],
                    location_name=details["location_name"],
                    location_type=details["location_type"],
                    street_address=details["street_address"],
                    city=details["city"],
                    zip_postal=details["zip_postal"],
                    state=details["state"],
                    country_code=details["country_code"],
                    phone=details["phone"],
                    latitude=details["latitude"],
                    longitude=details["longitude"],
                    hours_of_operation=details["hours_of_operation"],
                    raw_address=raw_address,
                )


def scrape():
    start = time.time()
    logger.info("Started")
    count = 0
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    logger.info(f"Total row added = {count}")
    logger.info(f"Scrape took {end-start} seconds.")


session.close()
if __name__ == "__main__":
    scrape()
