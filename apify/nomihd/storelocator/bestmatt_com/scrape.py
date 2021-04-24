# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "bestmatt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bestmatt.com/find-store"
    base = search_url[::-1].split("/", 1)[1][::-1]
    search_res = session.get(url=search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    centers = search_sel.xpath('//div[contains(@class,"location-box")]')

    for center in centers:
        broken_url = "".join(center.xpath("./a[1]/@href"))

        locator_domain = website

        location_name = "".join(center.xpath("./a[1]/text()"))

        raw_address = center.xpath('.//a[@class="l-add"]/text()')

        street_address = raw_address[0].strip()

        city = raw_address[1].strip().split(",")[0].strip()
        state = raw_address[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = raw_address[1].strip().split(",")[1].strip().split(" ")[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = "".join(center.xpath('.//a[@class="l-phone"]/text()')).strip()

        center_page_link = broken_url if "http" in broken_url else (base + broken_url)

        # --------------------------------------------
        log.info(center_page_link)
        page_res = session.get(center_page_link, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        hrs_str = " ".join(
            page_sel.xpath(
                '//div[contains(@class,"container")]//node()[contains(text(),"Monday") or contains(text(), "Saturday") or contains(text(), "Sunday")]//text()'
            )
        )
        hrs_str = (
            hrs_str.replace("  ", " ")
            .strip()
            .replace("PM ", "PM; ")
            .replace("losed ", "losed; ")
            .replace("\n", "")
        )
        hours_of_operation = hrs_str

        lat_lng = "".join(center.xpath('.//a[@class="l-add"]/@href'))
        if "maps?ll=" in lat_lng:
            lat_lng = lat_lng.split("maps?ll=")[1].split("&")[0]
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        else:
            lat_lng = (
                lat_lng.split(",14z/data")[0].split("@")[1]
                if ",14z/data" in lat_lng
                else lat_lng.split(",17z/data")[0].split("@")[1]
            )
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        raw_address = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=center_page_link,
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
