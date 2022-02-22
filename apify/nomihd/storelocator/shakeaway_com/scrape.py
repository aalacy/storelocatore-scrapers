# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "shakeaway.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    urls_list = [
        "https://shakeaway.com/index.php/shops/international-stores",
        "https://www.shakeaway.com/index.php/all-stores/item/bournemouth",
    ]
    with SgRequests() as session:
        for search_url in urls_list:
            stores_req = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//div[@class="customuk_title"]/form/select/option[position()>1]/@value'
            )
            if len(stores) <= 0:
                stores = stores_sel.xpath('//div[@id="intstores"]//a/@href')

            for store in stores:
                if "#" == store:
                    break

                page_url = (
                    "https://www.shakeaway.com/index.php/all-stores/item/"
                    + store.replace("/index.php/all-stores/item/", "").strip()
                )
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                locator_domain = website
                location_name = "".join(
                    store_sel.xpath('//h1[@class="pos-title"]/text()')
                ).strip()

                if "international-stores" not in search_url:
                    country_code = "GB"
                    sections = store_sel.xpath("//p")

                    for index in range(0, len(sections)):
                        if (
                            "Address"
                            in "".join(sections[index].xpath(".//text()")).strip()
                        ):
                            raw_address = ", ".join(
                                sections[index + 1].xpath("span/text()")
                            ).strip()
                            if len(raw_address) <= 0:
                                raw_address = ", ".join(
                                    sections[index + 1].xpath("text()")
                                ).strip()
                                if len(raw_address) <= 0:
                                    raw_address = ", ".join(
                                        sections[index + 1].xpath("span/span/text()")
                                    ).strip()
                        if (
                            "Phone Number"
                            in "".join(sections[index].xpath(".//text()")).strip()
                        ):
                            phone = "".join(
                                sections[index + 1].xpath("span/text()")
                            ).strip()
                            if phone == "TBC":
                                phone = ""

                    formatted_addr = parser.parse_address_intl(
                        raw_address.replace(",,", ",")
                    )
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    if street_address == "26":
                        street_address = ", ".join(raw_address.split(",")[:-2])

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode
                    if zip is None:
                        zip = raw_address.split(",")[-1].strip()

                    hours = store_sel.xpath("//table//tr/td[1]/p[2]/span")
                    hours_list = []
                    if len(hours) > 0:
                        for hour in hours:
                            hours_list.append(
                                "".join(hour.xpath(".//text()"))
                                .strip()
                                .replace(" - ", ":")
                                .strip()
                            )
                    else:
                        hours = store_sel.xpath("//table//tr/td[1]/p[2]/text()")

                    hours_of_operation = (
                        "; ".join(hours_list)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )

                    if len(hours_of_operation) <= 0:
                        hours = store_sel.xpath("//table//tr/td[1]//text()")

                        for hour in hours:
                            hours_list.append("".join(hour).strip())

                        hours_of_operation = (
                            "; ".join(hours_list)
                            .strip()
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "-")
                            .strip()
                            .replace("; Opening Times; ; ;", "")
                            .strip()
                        )

                else:
                    country_code = location_name.split(",")[-1].strip()
                    raw_info = store_sel.xpath("//table//tr[2]/td[1]//text()")
                    raw_list = []
                    for raw in raw_info:
                        if len("".join(raw).strip()) > 0:
                            raw_list.append("".join(raw).strip())

                    raw_address = ", ".join(raw_list[1:-2]).strip()
                    phone = raw_list[-1].strip()
                    if phone == "TBC" or phone == "Coming soon":
                        phone = "<MISSING>"

                    formatted_addr = parser.parse_address_intl(
                        raw_address.replace(",,", ",")
                    )
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    if street_address and street_address == "38":
                        street_address = "Building 38"

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    days = store_sel.xpath("//table//tr[2]/td[2]//text()")
                    raw_time = store_sel.xpath("//table//tr[2]/td[3]/p")
                    days_list = []
                    time_list = []
                    for d in days:
                        if len("".join(d).strip()) > 0:
                            days_list.append("".join(d).strip())

                    for t in raw_time:
                        if len("".join(t.xpath(".//text()")).strip()) > 0:
                            time_list.append("".join(t.xpath(".//text()")).strip())

                    hours_list = []
                    if len(days_list) == len(time_list):
                        for index in range(0, len(days_list)):
                            hours_list.append(days_list[index] + ":" + time_list[index])

                    hours_of_operation = "; ".join(hours_list).strip()

                location_type = "<MISSING>"
                if "our stores are temporarily closed" in store_req.text:
                    location_type = "temporarily closed"

                store_number = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"
                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
                ).strip()
                if len(map_link) > 0:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

                if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
                    hours_of_operation = "".join(hours_of_operation[:-1]).strip()

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
                    hours_of_operation=hours_of_operation.replace("; ;", "")
                    .strip()
                    .replace("; 0", "0")
                    .strip(),
                    raw_address=raw_address,
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
