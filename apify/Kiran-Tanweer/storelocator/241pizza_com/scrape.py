from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "123pizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers_cities = {
    "authority": "241pizza.com",
    "method": "POST",
    "path": "/src/themes/twoforone/lib/php/ajax.php",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded",
    "endpoint": "getcities_prov.pvp",
    "origin": "https://241pizza.com",
    "prefix": "TFO",
    "referer": "https://241pizza.com/restaurant-locator/",
    "url": "https://chairmanbrands.impellent.app/v1/locations/cities.php",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
}
headers_stores = {
    "authority": "241pizza.com",
    "method": "POST",
    "path": "/src/themes/twoforone/lib/php/ajax.php",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded",
    "endpoint": "getstores_city.pvp",
    "origin": "https://241pizza.com",
    "prefix": "TFO",
    "referer": "https://241pizza.com/restaurant-locator/",
    "url": "https://chairmanbrands.impellent.app/v1/locations/stores.php",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
}


def store_data(loc):
    location_name = loc["location"]
    store_number = loc["store_number"]
    latitude = loc["latitude"]
    longitude = loc["longitude"]
    phone = loc["phone"]
    hours_of_operation = (
        str(loc["hours"])
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
        .replace(": open: ", " ")
        .replace(", close: ", " - ")
    )
    street_address = loc["address"]
    city = loc["city"]
    zip_postal = loc["postal"]
    return (
        location_name,
        store_number,
        latitude,
        longitude,
        phone,
        hours_of_operation,
        street_address,
        city,
        zip_postal,
    )


def fetch_data():
    if True:
        loclist = []
        statelist = []
        url = "https://241pizza.com/src/themes/twoforone/lib/php/ajax.php"
        province_list = session.post(url, headers=headers_cities).json()["response"][
            "province"
        ]
        for province in province_list:
            cities = province["cities"]
            cities = cities["city"]
            if type(cities) is list:
                for city in cities:
                    loclist.append(city)
            else:
                loclist.append(cities)
            state = province["name"]
            if isinstance(cities, list) == True:
                length = len(cities)
                i = 0
                for i in range(0, length):
                    statelist.append(state)
            else:
                statelist.append(state)

        for loc, state in zip(loclist, statelist):
            page_url = (
                "https://241pizza.com/restaurant-locator/#!/province/"
                + state.strip().lower()
                + "/city/"
                + loc.strip().lower()
                + "/"
            )
            log.info(page_url)
            payload = {"city": loc}
            loc = session.post(url, data=payload, headers=headers_stores).json()[
                "response"
            ]["city"]["store"]
            if type(loc) is list:
                stores = loc
                for store in stores:
                    (
                        location_name,
                        store_number,
                        latitude,
                        longitude,
                        phone,
                        hours_of_operation,
                        street_address,
                        city,
                        zip_postal,
                    ) = store_data(store)
                    yield SgRecord(
                        locator_domain="https://241pizza.com/",
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state,
                        zip_postal=zip_postal.strip(),
                        country_code="CA",
                        store_number=store_number,
                        phone=phone,
                        location_type="<MISSING>",
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation.strip(),
                    )
            else:
                (
                    location_name,
                    store_number,
                    latitude,
                    longitude,
                    phone,
                    hours_of_operation,
                    street_address,
                    city,
                    zip_postal,
                ) = store_data(loc)
                yield SgRecord(
                    locator_domain="https://241pizza.com/",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state,
                    zip_postal=zip_postal.strip(),
                    country_code="CA",
                    store_number=store_number,
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
