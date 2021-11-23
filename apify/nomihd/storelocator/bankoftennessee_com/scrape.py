# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "bankoftennessee.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bankoftennessee.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//h3[@class="location-heading"]/a/@href')
    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath(
                '//div[@class="text-center col-sm-12 col-md-8 col-md-offset-2"]/h2/text()'
            )
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website
        street_address = "<MISSING>"
        state = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        address = ""
        hours = ""
        sections = store_sel.xpath('//div[@class="col-sm-3 col-ms-6"]')
        for section in sections:
            if "Address" in "".join(section.xpath("h3/text()")).strip():
                address = "".join(section.xpath("p/text()")).strip().split(",")

            if "Phone" in "".join(section.xpath("h3/text()")).strip():
                phone = "".join(section.xpath("p/text()")).strip()

            if "Hours" in "".join(section.xpath("h3/text()")).strip():
                hours = section.xpath("p/text()")

        hours_list = []
        for temp in hours:
            if len("".join(temp).strip()) > 0:
                if "Lobby" in "".join(temp).strip():
                    continue
                if "Drive Thru" in "".join(temp).strip():
                    break

                hours_list.append("".join(temp).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        try:
            hours_of_operation = hours_of_operation.split("; Drive-up")[0].strip()
        except:
            pass

        if len(address) >= 3:
            street_address = ", ".join(address[:-2]).strip()

            city = address[-2].strip()
            state = address[-1].strip().split(" ")[0].strip()
            zipp = address[-1].strip().split(" ")[-1].strip()

        elif "Mt. Juliet" in "".join(address):
            street_address = (
                ", ".join(address[:-1]).strip().replace("Mt. Juliet", "").strip()
            )
            city = "Mt. Juliet"
            state = address[-1].strip().split(" ")[0].strip()
            zipp = address[-1].strip().split(" ")[-1].strip()

        country_code = "US"
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()

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
            zip_postal=zipp,
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
