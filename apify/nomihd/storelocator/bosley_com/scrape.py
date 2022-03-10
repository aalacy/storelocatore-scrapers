# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bosley.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.bosley.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bosley.com/locations/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//p/a[contains(text(),"Location Details")]/@href')
        for store_url in stores:
            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(store_sel.xpath("//h1/text()")).strip()
            add_list = store_sel.xpath(
                '//div[./h4/span[contains(@class,"icon-location")]]/p/text()'
            )

            city_state_zip_index = -1
            city_state_zip = ""
            for add in range(0, len(add_list)):
                if ", " in add_list[add] and "Suite" not in add_list[add]:
                    city_state_zip = add_list[add]
                    city_state_zip_index = add
                    break
            if city_state_zip_index == -1:
                street_address = ",".join(add_list[:-1]).replace(",,", ",").strip()
                city_state_zip = add_list[-1]
                city = city_state_zip.split(" ")[0].strip()
                state = city_state_zip.split(" ")[1].strip()
                zip = city_state_zip.split(" ")[2].strip()

            else:
                street_address = (
                    ",".join(add_list[:city_state_zip_index]).replace(",,", ",").strip()
                )
                city = city_state_zip.split(",")[0].strip()
                state = (
                    city_state_zip.split(",", 1)[1]
                    .strip()
                    .split(" ")[0]
                    .strip()
                    .replace(",", "")
                    .strip()
                )
                zip = city_state_zip.split(",", 1)[1].strip().split(" ")[1].strip()

            if len(street_address) <= 0:
                street_address = "".join(add_list).strip().split(",")[0].strip()
                city = location_name.replace("Bosley", "").strip()
                street_address = street_address.split(city)[0].strip()
                state = (
                    "".join(add_list)
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                    .strip()
                )
                zip = (
                    "".join(add_list)
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                    .strip()
                )

            country_code = "US"
            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath(
                    '//div[./h4/span[contains(@class,"icon-phone")]]/p//text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[./h4/span[contains(@class,"icon-watch")]]/p//text()'
                    )
                )
                .strip()
                .split("(")[0]
                .strip()
                .split("By Appointment Only")[0]
                .strip()
                .replace(";  ;", ";")
                .strip()
                .replace("day;", "day:")
                .replace("day ;", "day:")
                .strip()
            )

            if "Hours:" in hours_of_operation:
                hours_of_operation = (
                    hours_of_operation.split("Hours:")[1].strip().split("By")[0].strip()
                )

            if "Event Dates" in hours_of_operation:
                hours_of_operation = "<MISSING>"

            if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            map_link = store_sel.xpath(
                '//img[contains(@data-src-cmplz,"maps")]/@data-src-cmplz'
            )
            latitude = ""
            longitude = ""
            if len(map_link) > 0:
                latitude = (
                    map_link[0]
                    .split("?center=")[1]
                    .strip()
                    .split("&")[0]
                    .strip()
                    .split("%2C")[0]
                    .strip()
                )
                longitude = (
                    map_link[0]
                    .split("?center=")[1]
                    .strip()
                    .split("&")[0]
                    .strip()
                    .split("%2C")[1]
                    .strip()
                )
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
