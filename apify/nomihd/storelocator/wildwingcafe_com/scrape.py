# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wildwingcafe.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.wildwingcafe.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@id="comp-kff079nf3"]/ul/li/a/@href')
    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            list(
                set(
                    store_sel.xpath(
                        "//section[2]//node()[./h2//span[contains(@style,'bold')]]//text()"
                    )
                )
            )
        ).strip()
        if (
            len(location_name) <= 0
            or location_name == "Happy Hour"
            or location_name == "Open Hours"
        ):
            location_name = store_sel.xpath(
                "//h2[.//span[@style='font-weight:bold']]//text()"
            )
            if len(location_name) > 0:
                location_name = location_name[0]

        address = "".join(
            store_sel.xpath("//section//node()[./h2/a[contains(@href,'maps')]]//text()")
        ).strip()
        if len(address) <= 0:
            address = store_sel.xpath("//*[./h2/a[contains(@href,'maps')]]//text()")
            if len(address) > 0:
                address = address[0]

        street_address = (
            ", ".join(address.split(",")[:-2])
            .strip()
            .replace("The Gardens at Westgreen,", "")
            .strip()
            .replace("The Shoppes at River Crossing,", "")
            .strip()
        )
        city = address.split(",")[-2]
        state = address.split(",")[-1].strip().split(" ")[0].strip()
        zip = address.split(",")[-1].strip().split(" ")[1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(
                store_sel.xpath(
                    "//section//node()[./h2/span[not(.//span[contains(@style,'bold')])]]//text()"
                )
            )
            .strip()
            .replace("Phone:", "")
            .strip()
        )
        if len(phone) <= 0:
            raw_info = list(set(store_sel.xpath("//h2[@class='font_4']//text()")))
            for ph in raw_info:
                if "(" in ph and ")" in ph:
                    phone = ph
                    break

        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath("//section//a[contains(@href,'maps')]/@href")
        ).strip()
        if len(map_link) > 0:
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        "//section//node()[./div/h2/span[contains(.//text(),'Open Hours')]]/div[last()]//text()"
                    )
                ],
            )
        )
        hours_list = []
        for hour in hours:
            if (
                "Sunday" in hour
                or "Monday" in hour
                or "Tuesday" in hour
                or "Wednesday" in hour
                or "Thursday" in hour
                or "Friday" in hour
                or "Saturday" in hour
                or "Everyday" in hour
                or "Daily" in hour
                or "Midnight" in hour
            ):
                hours_list.append(hour)

        hours_of_operation = "; ".join(hours_list).strip().replace("-;", "-").strip()

        if location_name == "Feast your eyes on our Menu and our Music":
            location_name = "CHARLOTTE UNIVERSITY CITY, NORTH CAROLINA"
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
