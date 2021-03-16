# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "bsnb_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://bsnb.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-6"][1]/p[position()>1]/a/@href')
    for store_url in stores:
        page_url = "https://bsnb.com/locations/" + store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//div[@id="banner-inner"]/h1/text()')
        ).strip()

        address = store_sel.xpath('//div[@class="col-sm-4"][1]/p[1]/strong/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        if len(add_list) == 1:
            add_list.append(
                "".join(
                    store_sel.xpath('//div[@class="col-sm-4"][1]/p[2]/strong/text()')
                ).strip()
            )

        street_address = ", ".join(add_list[:-1]).strip()
        city_state_zip = add_list[-1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"
        phone = ""
        raw_text = store_sel.xpath('//div[@class="col-sm-4"][1]/p')
        phone_list = []
        for temp in raw_text:
            if "Phone:" in "".join(temp.xpath("text()")).strip():
                phone_list = temp.xpath("text()")

        for ph in phone_list:
            if "Phone:" in "".join(ph).strip():
                phone = "".join(ph).strip().replace("Phone:", "").strip()

        hours_of_operation = "<MISSING>"
        hours = store_sel.xpath('//div[@class="col-sm-4"][1]/table')
        if len(hours) > 0:
            hours = hours[-1].xpath(".//tr")
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            if len(day) > 0:
                hours_list.append(day + ":" + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
