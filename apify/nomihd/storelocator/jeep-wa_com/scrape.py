# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import lxml.html

website = "jeep-wa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "jeep-wa.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://jeep-wa.com/trouver-un-concessionnaire/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        countries_dict = {}
        areas = search_sel.xpath('//select[@name="form_dealer"]/option[position()>1]')
        for area in areas:
            countries_dict["".join(area.xpath("@value")).strip()] = "".join(
                area.xpath("text()")
            ).strip()

        stores = search_sel.xpath('//div[@class="goweb-dealers"]/div')

        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = store.xpath("div[@class='dealer__holder']/h2/text()")
            if len(location_name) <= 0:
                location_name = store.xpath("div[@class='dealer__holder']/h4/text()")

            store_info = store.xpath("div[@class='dealer__holder']/div//text()")
            if len(store_info) <= 0:
                store_info = store.xpath("div[@class='dealer__holder']/p//text()")

            store_info_list = []
            for info in store_info:
                if len("".join(info).strip()) > 0:
                    store_info_list.append("".join(info).strip())

            street_address = ""
            city = ""
            state = "<MISSING>"
            zip = "<MISSING>"
            phone = "<MISSING>"
            country_code = countries_dict[
                "".join(store.xpath("@id")).strip().replace("goweb-dealer-", "").strip()
            ]

            store_number = (
                "".join(store.xpath("@id")).strip().replace("goweb-dealer-", "").strip()
            )

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude, longitude = "<MISSING>", "<MISSING>"

            if len(location_name) > 1:
                temp_addresses = (
                    ", ".join(store_info_list).strip().split("Localisation")
                )
                loc_name_list = location_name
                for index in range(0, len(loc_name_list)):
                    location_name = loc_name_list[index]
                    store_info_list = temp_addresses[index].split(",")
                    add_list = []
                    for info in store_info_list:
                        if len("".join(info).strip()) > 0:
                            if (
                                "Tél:" in "".join(info).strip()
                                or "Phone" in "".join(info).strip()
                                or "Tel:" in "".join(info).strip()
                            ):
                                phone = (
                                    "".join(info)
                                    .strip()
                                    .replace("Phone", "")
                                    .strip()
                                    .replace("Tél:", "")
                                    .strip()
                                    .replace("Tel:", "")
                                    .strip()
                                    .split("/")[0]
                                    .strip()
                                    .replace(":", "")
                                    .strip()
                                    .split("|")[0]
                                    .strip()
                                    .split("-")[0]
                                    .strip()
                                )
                                break
                            else:
                                if (
                                    '"N' not in "".join(info).strip()
                                    and '"W' not in "".join(info).strip()
                                ):
                                    add_list.append("".join(info).strip())

                    raw_address = ", ".join(add_list).strip().replace(",,", ",").strip()
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = "<MISSING>"

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
                        raw_address=raw_address,
                    )

            else:
                location_name = "".join(location_name).strip()
                add_list = []
                for info in store_info_list:
                    if (
                        "Tél:" in "".join(info).strip()
                        or "Phone" in "".join(info).strip()
                    ):
                        phone = (
                            "".join(info)
                            .strip()
                            .replace("Phone", "")
                            .strip()
                            .replace("Tél:", "")
                            .strip()
                            .split("/")[0]
                            .strip()
                            .replace(":", "")
                            .strip()
                            .split("|")[0]
                            .strip()
                            .split("-")[0]
                            .strip()
                        )
                        break
                    else:
                        add_list.append("".join(info).strip())

                raw_address = ", ".join(add_list).strip().replace(",,", ",").strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = "<MISSING>"

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
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
