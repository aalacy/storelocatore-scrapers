# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "pizzahut.jp",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

API_HEADERS = {
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Client": "606dd890-1e5d-4898-853a-0ef434fff627",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.pizzahut.jp/",
    "Lang": "en",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.jp/sitemap.xml"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        links = search_res.text.split("<loc>")

        for index in range(1, len(links)):
            page_url = links[index].split("</loc>")[0].strip()
            if "pizzahut.jp/huts/" not in page_url:
                continue

            store_number = page_url.split("/")[-1].strip()

            locator_domain = website

            log.info(f"pulling data for store ID: {store_number}")
            params = (
                ("code", store_number),
                ("with", "openingHours,specialDates,hutDays,lunchTimes,publicHoliday"),
            )
            try:
                store_req = SgRequests.raise_on_err(
                    session.get(
                        f"https://apiapne1.phdvasia.com/v1/product-hut-fe/outlets/detail/{store_number}",
                        headers=API_HEADERS,
                        params=params,
                    )
                )

                store_info = json.loads(store_req.text)["data"]["item"]
                if len(store_info) <= 0:
                    continue

                raw_address = store_info["address"]
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                try:
                    if street_address.replace("-", "").strip().isdigit():
                        street_address = raw_address.split(",")[0].strip()
                        if street_address.replace("-", "").strip().isdigit():
                            street_address = raw_address.split(",")[:2].strip()
                except:
                    pass

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "JP"

                location_name = store_info["name"]

                phone = store_info["phone"]

                location_type = "<MISSING>"
                hours = store_info["opening_hours"]
                hours_list = []
                for hour in hours:
                    if hour["order_type"][0] == "D":
                        if hour["active"] == 1:
                            day = hour["day"]
                            time = hour["opening"] + " - " + hour["closing"]
                            hours_list.append(day + ": " + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .replace("配達・お持ち帰り; ", "")
                    .replace(":;", ":")
                    .strip()
                )

                latitude, longitude = store_info["lat"], store_info["long"]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            except SgRequestError as e:
                log.error(e.status_code)


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
