# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "mariasitaliankitchen.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://mariasitaliankitchen.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = list(
        set(
            stores_sel.xpath(
                '//a[contains(text(),"(Info, Directions and Pictures)")]/@href'
            )
        )
    )

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = "".join(store_sel.xpath("//div/h5//text()")).strip()

        address = store_sel.xpath('//div[@class="organic-column one-half"]/text()')
        if len("".join(address).strip()) <= 0:
            address = store_sel.xpath(
                '//div[@class="organic-column one-half"]/p[1]/text()'
            )
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = ", ".join(add_list[:-3]).strip()
        city = add_list[-3].strip().split(",")[0].strip()
        if len(add_list[-3].strip().split(",")[1].strip().split(" ")) == 2:
            state = add_list[-3].strip().split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[-3].strip().split(",")[1].strip().split(" ")[-1].strip()
        else:
            state = city.rsplit(" ", 1)[-1].strip()
            city = city.replace(state, "").strip()
            zip = add_list[-3].strip().split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = add_list[-2].strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = (
            "; ".join(
                " ".join(
                    store_sel.xpath(
                        '//div[@class="organic-column one-half last"]//text()'
                    )
                )
                .strip()
                .replace("HOURS", "")
                .strip()
                .split("\n")
            )
            .strip()
            .replace(";  Wine/Beer available.", "")
            .strip()
        )

        if (
            len(hours_of_operation) <= 0
            or "The Original Location" in hours_of_operation
        ):
            sections = store_sel.xpath('//div[@class="organic-column one-half"]/p')
            for index in range(0, len(sections)):
                if (
                    "HOURS"
                    in "".join(
                        sections[index].xpath('span[@class="reddish"]/text()')
                    ).strip()
                ):
                    hours_of_operation = (
                        "; ".join(
                            " ".join(sections[index].xpath(".//text()"))
                            .strip()
                            .replace("HOURS", "")
                            .strip()
                            .split("\n")
                        )
                        .strip()
                        .replace(";  Wine/Beer available.", "")
                        .strip()
                    )
                    break

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(store_sel.xpath('//a[contains(text(),"Map")]/@href')).strip()
        if len(map_link) > 0:
            if "?lat=" in map_link:
                latitude = map_link.split("?lat=")[1].strip().split("&")[0].strip()
                longitude = map_link.split("&lon=")[1].strip().split("&")[0]
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
