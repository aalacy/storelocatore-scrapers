# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "thereefstores.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.thereefstores.com",
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
    search_url = "http://www.thereefstores.com"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//section[.//div[ ./p[contains(@style,"13px; line-height:1.6em")]]]'
    )

    for store in store_list:

        page_url = search_url

        locator_domain = website

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/div[ ./p[contains(@style,"13px; line-height:1.6em")]]/p//text()'
                    )
                ],
            )
        )

        full_address = store_info[0].strip()

        street_address = ", ".join(full_address.split(",")[:-2]).strip()
        city = full_address.split(",")[-2].strip()
        state = full_address.split(",")[-1].strip().split(" ")[0].strip()
        zip = full_address.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"

        location_name = "".join(store.xpath(".//h2//text()")).strip()

        phone = " ".join(store_info[1:]).split("•")[1].strip(" \u200b").strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = (
            " ".join(store_info[1:])
            .split("•")[0]
            .strip(" \u200b")
            .strip()
            .replace(" PM", "PM")
            .replace(" AM", "AM")
            .replace("PM ", "PM; ")
        )
        map_link = "".join(store.xpath('.//a[contains(@href,"maps")]/@href'))

        latitude, longitude = get_latlng(map_link)

        raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
