# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "cruawinebar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    """ US LOCATIONS """

    search_url = "https://cruwinebar.com/locations-2/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="wpb_wrapper"]/a[contains(text(),"Location Details")]/@href'
    )

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = "".join(
            store_sel.xpath(
                '//div[@class="title_subtitle_holder title_content_background"]/h1//text()'
            )
        ).strip()

        address = "".join(
            store_sel.xpath('//li[contains(text(),"Our address is")]/a/text()')
        ).strip()
        if address == "1442 Larimer St., Denver CO. 80202":
            address = address.replace(
                "1442 Larimer St., Denver CO. 80202",
                "1442 Larimer St., Denver, CO 80202",
            ).strip()
        street_address = ", ".join(address.split(",")[:-2])
        city = address.split(",")[-2].strip()
        state = address.split(",")[-1].strip().split(" ")[0].strip()
        zip = address.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = (
            "".join(
                store_sel.xpath('//li[contains(text(),"Call us anytime at")]//text()')
            )
            .strip()
            .replace(":", "")
            .replace("Call us anytime at", "")
            .strip()
        )

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        temp_hours = store_sel.xpath('//table[contains(@id,"tablepress-")]//tr')
        hours_list = []
        for temp in temp_hours:
            if "WINE BAR" in "".join(temp.xpath("td[1]/text()")).strip():
                hours = temp.xpath("td[position()>1]")
                for hour in hours:
                    day = "".join(hour.xpath("b/text()")).strip()
                    time = "".join(hour.xpath("text()")).strip()
                    hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//li[contains(text(),"Our address is")]/a/@href')
        ).strip()
        if len(map_link) > 0:
            if "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]
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
