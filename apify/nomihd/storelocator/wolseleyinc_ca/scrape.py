# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wolseleyinc.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    elif "daddr=" in map_link:
        latitude = map_link.split("daddr=")[1].split(",")[0].strip()
        longitude = map_link.split("daddr=")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://info.wolseleyexpress.com/en/branch-locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//div[@class="hs-accordion__item"]')

        for _state in states:

            state = "".join(_state.xpath("./button/text()")).strip()
            log.info(state)

            stores = _state.xpath(".//table//tr")

            for no, store in enumerate(stores[1:], 1):

                locator_domain = website

                page_url = search_url

                store_number = "<MISSING>"

                location_name = "".join(store.xpath("./td[1]/p[1]//text()")).strip()
                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str, [x.strip() for x in store.xpath("./td[1]/p[2]//text()")]
                    )
                )
                if len(store_info) <= 0:
                    store_info = list(
                        filter(
                            str,
                            [x.strip() for x in store.xpath("./td[1]/p[1]//text()")],
                        )
                    )
                    location_name = "".join(store.xpath("./td[1]/span/text()"))
                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)

                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                zip = formatted_addr.postcode
                country_code = "CA"

                temp_phone = store.xpath(".//td[2]//text()")
                phone_list = []
                for ph in temp_phone:
                    if len("".join(ph).strip()) > 0:
                        phone_list.append("".join(ph).strip())

                if len(phone_list) > 0:
                    if phone_list[0] == "(":
                        phone = "".join(phone_list[:2]).strip()
                    else:
                        phone = phone_list[0]
                else:
                    phone = "<MISSING>"

                hours_of_operation = "<MISSING>"

                map_link = "".join(store.xpath('.//a[contains(@href,"maps")]/@href'))

                latitude, longitude = get_latlng(map_link)

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
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
