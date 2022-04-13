# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "r_bank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.r.bank/about/convenient-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="row row-loc"]')
    latlngList = stores_req.text.split("google.maps.LatLng(")[2:]
    for index, store in enumerate(stores, 0):
        page_url = search_url

        location_name = "".join(store.xpath("div[1]/h2/text()")).strip()
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        "div[3]//div[@class='large-12 medium-12 small-16 columns']//a[1]/text()"
                    )
                ],
            )
        )

        street_address = (
            ", ".join(raw_address[:-1])
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
            .replace("3000,  ", "3000 ")
            .strip()
        )
        city_state_zip = "".join(raw_address[-1]).strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        phone = store.xpath(
            'div[3]//div[./h3[contains(text(),"Contact")]]/p[contains(text(),"Phone:")]/text()'
        )
        try:
            phone = phone[0].replace("Phone:", "").strip()
        except:
            pass

        if phone == "":
            phone = "".join(
                store.xpath(
                    'div[3]//div[./h3[contains(text(),"Contact")]]/p[contains(text(),"Phone:")]/font/text()'
                )
            ).strip()

        hours_of_operation = (
            "; ".join(
                filter(
                    str,
                    store.xpath(
                        'div[3]//div[./h3[contains(text(),"Lobby Hours")]]/p/text()'
                    ),
                )
            )
            .strip()
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation[-1] == ";":
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

        latlng = latlngList[index].split(");")[0].strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[1].strip()

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
