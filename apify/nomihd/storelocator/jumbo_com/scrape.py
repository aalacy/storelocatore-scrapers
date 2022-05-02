# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "jumbo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.jumbo.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = {
    "address": "",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        home_req = session.get("https://www.jumbo.com/winkels", headers=headers)
        synchronizertoken = (
            home_req.text.split("var SYNCHRONIZER_TOKEN_VALUE = '")[1]
            .strip()
            .split("'")[0]
            .strip()
        )

        headers["synchronizertoken"] = synchronizertoken

        stores_req = session.get(
            "https://www.jumbo.com/INTERSHOP/rest/WFS/Jumbo-Grocery-Site/webapi/stores",
            headers=headers,
            params=params,
        )
        stores = json.loads(stores_req.text)["stores"]

        for store in stores:
            latitude = store["latitude"]
            longitude = store["longitude"]
            location_type = store["locationType"]
            locator_domain = website
            store_number = store["sapStoreID"]

            location_name = store["addressName"]
            page_url = (
                "https://www.jumbo.com/winkel/"
                + location_name.lower()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "")
                .strip()
                .replace("-", "")
                .replace(" ", "-")
                .strip()
                .replace("'", "")
                .strip()
                .replace(".", "")
                .strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError):
                continue

            store_sel = lxml.html.fromstring(store_req.text)
            street_address = store["street"] + " " + store["street2"]
            city = store["city"]
            state = "<MISSING>"
            zip = store["postalCode"]

            country_code = "BE"

            phone = "".join(
                store_sel.xpath('//jum-list-item[@icon="phone"]/text()')
            ).strip()
            log.info(phone)
            hours_list = []
            hours = store_sel.xpath('//div[@class="opening-hours__line"]')
            for hour in hours:
                day = "".join(hour.xpath("span[@class='day']/text()")).strip()
                time = "".join(hour.xpath("span[@class='time']/text()")).strip()
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
