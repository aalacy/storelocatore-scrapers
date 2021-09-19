# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "dysarts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.dysarts.com",
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


def validhour(x):
    if (
        ("AM" in x.upper() and "PM" in x.upper())
        or (re.search("\\d *[AP]M", x.upper()))
        or ("DAILY" in x.upper())
        or ("M" in x.upper() and ":" in x.upper())
        or ("TU" in x.upper() and ":" in x.upper())
        or ("WED" in x.upper() and ":" in x.upper())
        or ("TH" in x.upper() and ":" in x.upper())
        or ("F" in x.upper() and ":" in x.upper())
        or ("SA" in x.upper() and ":" in x.upper())
        or ("SU" in x.upper() and ":" in x.upper())
        or ("～" in x.upper())
        or ("-" in x.upper())
    ):

        if (
            "JAN" in x.upper()
            or "FEB" in x.upper()
            or "MAR" in x.upper()
            or "APR" in x.upper()
            or "MAY" in x.upper()
            or "JUN" in x.upper()
            or "JUL" in x.upper()
            or "AUG" in x.upper()
            or "SEP" in x.upper()
            or "OCT" in x.upper()
            or "NOV" in x.upper()
            or "DEC" in x.upper()
            or "HOLIDAY" in "".join(x.upper()[:7])  # Extra check for Holiday
            or "E-MAIL." in x.upper()
            or "E-MAIL:" in x.upper()
            or "PRIOR TO YOUR VISIT." in x.upper()
            or "IN-PERSON" in x.upper()
            or "IN-STORE" in x.upper()
        ):
            return False
        return True
    return False


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
    search_url = "https://www.dysarts.com/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[./*[@class="highway"]]')

    for store in store_list:

        page_url = "".join(store.xpath("./a/@href"))

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        store_info = list(
            filter(
                str,
                [x.strip() for x in store.xpath("./address//text()")],
            )
        )

        full_address = " ".join(store_info).strip()
        street_address = ",".join(full_address.split(",")[:-2]).strip()
        city = full_address.split(",")[-2].strip()
        state = full_address.split(",")[-1].strip().split(" ")[0].strip()
        zip = full_address.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"
        location_name = "".join(store.xpath("./strong//text()")).strip()
        phone = list(
            filter(
                str,
                [x.strip() for x in store.xpath('./div[@class="phone"]/text()')],
            )
        )
        phone = phone[-1].replace("Restaurant:", "").strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//*[contains(text(),"day")]//text()')
                ],
            )
        )

        hours = list(filter(validhour, hours))

        hours_of_operation = (
            "; ".join(hours).replace("Now Open!;", "").replace(":;", ":").strip()
        )
        if "curbside pickup." in hours_of_operation:
            hours_of_operation = hours_of_operation.split("curbside pickup.")[1].strip()
        map_link = "".join(store_sel.xpath('.//a[contains(@href,"maps")]/@href'))

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
