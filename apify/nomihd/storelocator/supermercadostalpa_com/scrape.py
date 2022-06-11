# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "supermercadostalpa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://supermercadostalpa.com/localidades/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = (
        "".join(
            stores_sel.xpath('//script[@id="frontend.dummy.popup-js-extra"]/text()')
        )
        .strip()
        .split("var ppsPopupsFromFooter = ")[1:]
    )
    for store in stores:
        json_str = store.split("}];")[0].strip() + "}]"
        store_sel = lxml.html.fromstring(
            json.loads(json_str)[0]["params"]["tpl"]["txt_0"]
        )

        map_link = "".join(store_sel.xpath("//iframe/@src")).strip()
        page_url = search_url

        locator_domain = website

        location_name = json.loads(json_str)[0]["label"]

        raw_list = (
            map_link.split("!2s")[1].strip().split(", USA!")[0].strip().split(",")
        )
        street_address = ""
        city = ""
        state = ""
        zip = ""

        if "Talpa Supermercados" in "".join(raw_list).strip():
            if location_name == "Lilburn":
                street_address = "4760 Lawrenceville Hwy"
                city = "Lilburn"
                state = "GA"
                zip = "30047"
            elif location_name == "Mableton":
                street_address = "1245 Veterans Memorial Hwy SW"
                city = "Mableton"
                state = "GA"
                zip = "30126"

        else:
            street_address = raw_list[0].strip().split("(")[0].strip()
            state_zip = raw_list[-1].strip()
            city = raw_list[-2].strip()
            state = state_zip.split(" ")[0].strip()
            zip = state_zip.split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "<MISSING>"

        location_type = "<MISSING>"
        hours_of_operation = " ".join(
            stores_sel.xpath(
                '//div[@class="elementor-widget-wrap"][.//span[contains(text(),"Horarios de Atenci")]]/div[2]//p/text()'
            )
        ).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
