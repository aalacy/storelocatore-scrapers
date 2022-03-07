# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "pizzahut.fi"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
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
    search_url = "https://pizzahut.fi/ravintolat/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    stores = search_sel.xpath(
        '//div[@class="col-sm-6 py-3 px-5 toimipiste_item"]/a/@href'
    )

    for store_url in stores:

        page_url = store_url
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        locator_domain = website
        location_name = "".join(store_sel.xpath("//div/h2/text()")).strip()

        temp_address = store_sel.xpath(
            '//div[./p[1][text()="Osoite"]]/p[position()>1]/text()'
        )
        add_list = []
        for temp in temp_address:
            if "p." != "".join(temp).strip():
                add_list.append("".join(temp).strip())
            else:
                break

        street_address = ", ".join(add_list[:-1]).strip()

        city = "<MISSING>"
        state = "<MISSING>"
        zip = "<MISSING>"
        if "," in add_list[-1].strip():
            city = add_list[-1].strip().split(",")[-1].strip()
            zip = add_list[-1].strip().split(",")[0].strip()
        else:
            city = add_list[-1].strip().split(" ")[-1].strip()
            zip = add_list[-1].strip().split(" ")[0].strip()

        if zip.isalpha():
            zip = "<MISSING>"

        country_code = "FI"

        phone = "".join(
            store_sel.xpath('//div[./p[1][text()="Osoite"]]/p/a/text()')
        ).strip()
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[./p[1][text()="Avoinna"]]/p[position()>1]/text()'
                    )
                ],
            )
        )
        if len(hours) <= 0:
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[./p[1][text()="Avoinna"]]/pre[1]/text()'
                        )
                    ],
                )
            )

        hours_of_operation = (
            "; ".join(hours)
            .strip()
            .replace("\r\n", "; ")
            .strip()
            .replace("\t", "")
            .strip()
            .replace("; ;", ";")
            .strip()
        )
        map_link = "".join(store_sel.xpath('//a[contains(@href,"maps/embed")]/@href'))

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
