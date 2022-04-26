# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "soulorigin.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.soulorigin.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.soulorigin.com.au",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.soulorigin.com.au/stores/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"action": "get_store_location", "search": ",AU", "region_dr": "all"}


def fetch_data():
    # Your scraper here
    api_url = "https://www.soulorigin.com.au/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)

        json_res = json.loads(api_res.text)

        stores = json_res["location_markers"]
        loc_list_html = json_res["location_list"]
        loc_list_sel = lxml.html.fromstring(loc_list_html)

        for no, store in enumerate(stores, 1):

            locator_domain = website
            location_name = store["title"].strip()
            store_number = store["store_id"]
            page_url = "".join(
                loc_list_sel.xpath(
                    f'//li[@id="li_{store_number}"]//a[contains(text(),"store details")]/@href'
                )
            )

            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath("//section//div[h1]/p//text()")
                    ],
                )
            )
            raw_address = ", ".join(store_info)

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state

            zip = formatted_addr.postcode

            country_code = "AU"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="phone"]/a[contains(@href,"tel:")]//text()'
                )
            )

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//h2[@class="time-title"]/..//li//text()'
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .replace("; -; ", " - ")
                .replace("mon; ", "mon: ")
                .replace("tue; ", "tue: ")
                .replace("wed; ", "wed: ")
                .replace("thu; ", "thu: ")
                .replace("fri; ", "fri: ")
                .replace("sat; ", "sat: ")
                .replace("sun; ", "sun: ")
            )

            latitude, longitude = store["lat"], store["lng"]
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
                raw_address=raw_address,
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
