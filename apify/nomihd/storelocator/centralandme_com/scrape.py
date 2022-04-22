# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "centralandme.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://centralandme.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://centralandme.com/store-locator/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//select[@id="ddstate"]/option[position()>1]')
        for st in states:
            state_val = "".join(st.xpath("@value")).strip()
            state = "".join(st.xpath("text()")).strip()
            data = {"action": "check_city", "state": state_val}

            cities_req = session.post(
                "https://centralandme.com/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
            )
            cities_sel = lxml.html.fromstring(cities_req.text)
            cities = cities_sel.xpath("//option[position()>1]")
            for cit in cities:
                city = "".join(cit.xpath("text()")).strip()
                city_val = "".join(cit.xpath("@value")).strip()

                page_url = (
                    "https://centralandme.com/store-locator/?state={}&city={}".format(
                        state_val, city_val
                    )
                )
                log.info(page_url)
                stores_req = session.get(page_url, headers=headers)
                stores_sel = lxml.html.fromstring(stores_req.text)
                stores = stores_sel.xpath(
                    "//div[@id='storelist']/div[@class='location-result']"
                )
                for store in stores:

                    locator_domain = website
                    store_number = "<MISSING>"

                    location_name = "".join(
                        store.xpath('div[@class="store-address"]/h4/text()')
                    ).strip()

                    location_type = "<MISSING>"

                    store_info = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store.xpath(
                                    'div[@class="store-address"]/p/text()'
                                )
                            ],
                        )
                    )

                    phone = "<MISSING>"

                    raw_address = "".join(store_info).strip()
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    zip = raw_address.split(",")[-1].strip()

                    if street_address:
                        street_address = (
                            street_address.replace(city, "")
                            .replace(state, "")
                            .replace(zip, "")
                            .strip()
                        )

                    country_code = "IN"

                    hours_of_operation = (
                        ", ".join(store.xpath('div[@class="store-address"]/h5/text()'))
                        .strip()
                        .replace("Store Time: ,", "")
                        .strip()
                        .replace("Store Time:", "")
                        .strip()
                    )

                    map_link = "".join(
                        store.xpath('div[@class="store-direction"]/iframe/@src')
                    ).strip()

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
