# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "pakmailcanada.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pakmailcanada.com",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def isvalid(x):

    if "WE HAVE MOVED" in x.upper():
        return False
    if "We look forward to being".upper() in x.upper():
        return False
    if "FOLLOW US" in x.upper():
        return False
    return True


def fetch_data():
    # Your scraper here
    base = "http://www.pakmailcanada.com"
    search_url = "http://www.pakmailcanada.com/pakmail-canada-locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath('//div[contains(@id,"Content")]//li//a/@href'))

    for store in store_list:

        page_url = base + store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = "".join(store_sel.xpath("//title/text()"))

        store_info = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[contains(@id,"Content")]//p[count(preceding-sibling::h3)=1]//text()'
                    )
                ],
            )
        )
        log.info(store_info)
        for phone_idx, x in enumerate(store_info):
            if "PHONE" in x.upper():
                break
        full_address = store_info[:phone_idx]

        full_address = list(filter(isvalid, full_address))

        street_address = " ".join(full_address[:-2])
        city = full_address[-2].split(",")[0].strip()
        state = full_address[-2].split(",")[1].strip()
        zip = full_address[-1].strip()
        country_code = "CA"
        store_number = "<MISSING>"

        phone = store_info[phone_idx + 1].replace("MAIL ", "").strip()

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[contains(@id,"Content")]//p[count(preceding-sibling::h3)=2]//text()'
                    )
                ],
            )
        )

        hours = list(filter(isvalid, hours))
        hours_of_operation = "; ".join(hours)

        map_link = "".join(store_sel.xpath('//iframe[contains(@src,"maps")]/@src'))

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
