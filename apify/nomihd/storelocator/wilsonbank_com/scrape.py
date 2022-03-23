# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wilsonbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.wilsonbank.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.wilsonbank.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.wilsonbank.com/about-us/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="card remove-blank location-card"]')
    for store in stores:
        temp_url = "".join(
            store.xpath('.//a[contains(text(),"See Location Details")]/@href')
        ).strip()
        page_url = "https://www.wilsonbank.com" + temp_url
        if len(temp_url) <= 0:
            continue
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if isinstance(
            store_req, SgRequestError
        ):  # incase page is broken, fetch from the main page.
            locator_domain = website
            store_number = "<MISSING>"
            location_name = "".join(store.xpath("div[1]/div[1]/div[1]/text()")).strip()

            raw_info = store.xpath(
                './/div[@class="card-body row"]/div[1]/div[1]/p/text()'
            )
            add_list = []
            phone = ""
            for r in raw_info:
                if "(" in r and ")" in r and "-" in r:
                    phone = r
                    break
                elif r.count("-") == 2:
                    phone = r
                else:
                    add_list.append("".join(r).strip())

            street_address = ", ".join(add_list[:-1]).strip()
            city = add_list[-1].strip().split(",")[0].strip()
            state = add_list[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = add_list[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"
            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    store.xpath('.//div[@class="card-body row"]/div[2]/div[1]/p/text()')
                )
                .strip()
                .replace("day;", "day:")
                .strip()
            )

            latitude, longitude = "<MISSING>", "<MISSING>"

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
        else:
            store_sel = lxml.html.fromstring(store_req.text)
            store_number = "<MISSING>"
            locator_domain = website

            location_name = "".join(
                store_sel.xpath("//h1[@class='page-title']/text()")
            ).strip()

            raw_info = store_sel.xpath(
                '//table[@class="table"]/tbody/tr[1]/td[1]//text()'
            )
            add_list = []
            phone = ""
            for r in raw_info:
                if "(" in r and ")" in r and "-" in r:
                    phone = r
                    break
                elif r.count("-") == 2:
                    phone = r

            for raw in raw_info:
                if (
                    "Get Directions" == raw
                    or "See Location Details" == raw
                    or "Opens in a new Window" in raw
                ):
                    break
                else:
                    if len("".join(raw).strip()) > 0:
                        add_list.append("".join(raw).strip())

            street_address = ", ".join(add_list[:-1]).strip()
            city = add_list[-1].strip().split(",")[0].strip()
            state = add_list[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = add_list[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"
            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    store_sel.xpath('//table[@class="table"]/tbody/tr[1]/td[2]//text()')
                )
                .strip()
                .replace("day;", "day:")
                .strip()
            )

            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()

            latitude, longitude = get_latlng(map_link)

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
