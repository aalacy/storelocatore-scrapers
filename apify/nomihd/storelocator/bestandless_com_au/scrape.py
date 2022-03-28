# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "bestandless.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.bestandless.com.au",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.bestandless.com.au/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bestandless.com.au/store-finder"
    with SgRequests() as session:
        home_req = session.get(search_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)
        csrf_token = "".join(
            home_sel.xpath('//input[@name="CSRFToken"]/@value')
        ).strip()

        states = session.get("https://www.bestandless.com.au/stores/states").json()
        for st in states.keys():
            data = {"state": st, "page": "0", "sort": "", "CSRFToken": csrf_token}
            stores_url = f"https://www.bestandless.com.au/stores/{st}"
            stores_req = session.post(stores_url, headers=headers, data=data)
            stores = json.loads(stores_req.text)["stores"]
            for store in stores:
                store_number = store["storeNumber"]
                page_url = "https://www.bestandless.com.au/" + store["url"]
                locator_domain = website
                location_name = store["name"]

                street_address = store["address"]["line1"]
                add_2 = store["address"]["line2"]
                if add_2 is not None and len(add_2) > 0:
                    street_address = street_address + ", " + add_2

                city = store["address"]["town"]
                state = st
                zip = store["address"]["postalCode"]

                country_code = "AU"
                phone = store["address"]["phone"]

                location_type = "<MISSING>"

                latitude = store["geoPoint"]["latitude"]
                longitude = store["geoPoint"]["longitude"]

                hours_of_operation = "<MISSING>"
                hours = store["openingHours"]["weekDayOpeningList"]
                hours_list = []
                for hour in hours:
                    day = hour["weekDay"]
                    if hour["closed"] is True:
                        time = "Closed"
                    else:
                        time = (
                            hour["openingTime"]["formattedHour"]
                            + " - "
                            + hour["closingTime"]["formattedHour"]
                        )

                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

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
