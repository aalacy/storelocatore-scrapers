# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wowcafe.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


params = (
    ("requesttype", "locator"),
    ("ref", "locations"),
)


def fetch_data():
    # Your scraper here
    api_url = "https://www.wowamericaneats.com/assets/includes/ajax/json.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, params=params)
        stores = json.loads(api_res.text)["features"]

        for store in stores:
            if str(store["properties"]["COMING_SOON"]) == "1":
                continue
            locator_domain = website
            location_name = store["properties"]["name"]
            store_number = store["id"]
            page_url = store["properties"]["LINK"]
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_type = "<MISSING>"

            street_address = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            if city == "NW, Washington, D.C":
                city = "Washington"

            state = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()

            if len(street_address) <= 0:
                raw_address = (
                    store["properties"]["ADDRESS"].replace("<br>", ",").strip()
                )
                street_address = ", ".join(raw_address.split(",")[:-2]).strip()
                city = raw_address.split(",")[-2].strip()
                state = raw_address.split(",")[-1].strip().split(" ")[0].strip()
                zip = raw_address.split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            phone = "".join(store_sel.xpath('//p/a[contains(@href,"tel:")]/text()'))

            hours = store_sel.xpath('//table[@class="table"]//tr')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]//text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                store["geometry"]["coordinates"][1],
                store["geometry"]["coordinates"][0],
            )
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
