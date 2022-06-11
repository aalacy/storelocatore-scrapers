import time

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

# F
MISSING = "<MISSING>"
DOMAIN = "acehardware.com"
website = "https://www.acehardware.com"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.acehardware.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "service-worker-navigation-preload": "true",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_mzvr=mXlhWQx5U0KbrKYEN08R8A; _gcl_au=1.1.1616117686.1620127562; _pin_unauth=dWlkPU5EVTVOVEl3TkRNdFpXSTJOeTAwTWpabExXSXlPVGd0WkRkak9HRTBOREUyT1dZeA;  _hjid=ddd4bcc5-b4b7-4c27-bc04-0a2e1b84cc74; _fbp=fb.1.1620127564810.919287347; OptanonAlertBoxClosed=2021-05-04T11:28:00.806Z;sb-sf-at-prod-s=at=bKKsDs1mqzLChnLp3UufIWR%2BWrJDsStFIzsXPnwTR%2F0Uw0vuOBFihrZxKSVHI1e%2F3AMH3eL5F4ihJENvX6nkAFgYT5WkTK9HviLlOD2mw8OUQMBaoHLyGQpCacYbjxxrs6oRxwyHauVhMc8qOSpl2%2BWx6oR5iSM7JaiAS9frpP3yR%2FahP3cbsOa8CdLY%2F1vCDY3bZtp9PNDBpXtbAaKCn5UDXkCzSSeSmX%2FTOZ9Q%2F7JO8Ft4JcOb96VydsXzaE5MVK1sW%2FhaywYwEMGjcrOiwUuwTg7EOk4lEesi2yQ7WyhIc7A3c1IE8e9dzWpZ7xnUANZwF0gH0L%2BC6z5Dv7wH0w%3D%3D&dt=2021-06-01T12%3A28%3A35.8321149Z;sb-sf-at-prod=at=bKKsDs1mqzLChnLp3UufIWR%2BWrJDsStFIzsXPnwTR%2F0Uw0vuOBFihrZxKSVHI1e%2F3AMH3eL5F4ihJENvX6nkAFgYT5WkTK9HviLlOD2mw8OUQMBaoHLyGQpCacYbjxxrs6oRxwyHauVhMc8qOSpl2%2BWx6oR5iSM7JaiAS9frpP3yR%2FahP3cbsOa8CdLY%2F1vCDY3bZtp9PNDBpXtbAaKCn5UDXkCzSSeSmX%2FTOZ9Q%2F7JO8Ft4JcOb96VydsXzaE5MVK1sW%2FhaywYwEMGjcrOiwUuwTg7EOk4lEesi2yQ7WyhIc7A3c1IE8e9dzWpZ7xnUANZwF0gH0L%2BC6z5Dv7wH0w%3D%3D;_mzvs=nn; _gid=GA1.2.2074316008.1622550517; IR_gbd=acehardware.com; _hjTLDTest=1;",
}

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def requests_with_retry(url):
    return session.get(url, headers=headers).json()


def fetchData():
    pages = 5000
    for x in range(0, pages, 1000):
        apiUrl = (
            "https://www.acehardware.com/api/commerce/storefront/locationUsageTypes/SP/locations?pageSize=1000&startIndex="
            + str(x)
        )
        jsonData = requests_with_retry(apiUrl)
        log.info(f"Total Locations: {len(jsonData['items'])}")
        for loc in jsonData["items"]:
            location_type = loc["locationTypes"][0]["name"] or MISSING
            store_number = loc["code"] or MISSING
            location_name = loc["name"] or MISSING
            street_address = loc["address"]["address1"] or MISSING
            city = loc["address"]["cityOrTown"] or MISSING
            state = loc["address"]["stateOrProvince"] or MISSING
            zip_postal = loc["address"]["postalOrZipCode"] or MISSING
            country_code = loc["address"]["countryCode"] or MISSING
            phone = loc["phone"] or MISSING
            latitude = loc["geo"]["lat"] or MISSING
            longitude = loc["geo"]["lng"] or MISSING
            page_url = "https://www.acehardware.com/store-details/" + str(store_number)
            log.info(f"Location Name: {location_name} & {page_url}")
            hours = loc["regularHours"]
            h = []
            for day in days:
                value = hours[f"{day.lower()}"]["label"]
                if value == "0000 - 0000":
                    value = "closed"
                h.append(f"{day}:{value}")
                hours_of_operation = "; ".join(h) or MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                location_type=location_type,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()

    with SgWriter() as writer:
        result = fetchData()
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
