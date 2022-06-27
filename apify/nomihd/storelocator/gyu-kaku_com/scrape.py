# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us
import re
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gyu-kaku.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def validhour(x):
    if (
        ("AM" in x.upper() and "PM" in x.upper())
        or (re.search("\\d *[AP]M", x.upper()))
        or ("DAILY" in x.upper())
        or ("EVERY DAY" in x.upper())
        or ("M" in x.upper() and ":" in x.upper())
        or ("TU" in x.upper() and ":" in x.upper())
        or ("WED" in x.upper() and ":" in x.upper())
        or ("TH" in x.upper() and ":" in x.upper())
        or ("F" in x.upper() and ":" in x.upper())
        or ("SA" in x.upper() and ":" in x.upper())
        or ("SU" in x.upper() and ":" in x.upper())
        or ("～" in x.upper())
        or ("-" in x.upper())
    ):

        if (
            "JAN" in x.upper()
            or "FEB" in x.upper()
            or "MAR" in x.upper()
            or "APR" in x.upper()
            or "MAY" in x.upper()
            or "JUN" in x.upper()
            or "JUL" in x.upper()
            or "AUG" in x.upper()
            or "SEP" in x.upper()
            or "OCT" in x.upper()
            or "NOV" in x.upper()
            or "DEC" in x.upper()
            or "HOLIDAY" in "".join(x.upper()[:7])  # Extra check for Holiday
            or "E-MAIL." in x.upper()
            or "E-MAIL:" in x.upper()
            or "PRIOR TO YOUR VISIT." in x.upper()
            or "IN-PERSON" in x.upper()
            or "IN-STORE" in x.upper()
            or "Due to COVID-19".upper() in x.upper()
            or "is currently offering".upper() in x.upper()
        ):
            return False
        return True
    return False


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()

    if not city or us.states.lookup(zip):
        city = city + " " + state
        state = zip
        zip = "<MISSING>"

    if city and state:
        if not us.states.lookup(state):
            city = city + " " + state
            state = "<MISSING>"

    country_code = "US"
    return street_address, city, state, zip, country_code


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
    base = "https://www.gyu-kaku.com"
    search_url = "https://www.gyu-kaku.com/locations-menus-2/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[contains(@class,"grid__item")]//a[not(img)]')

        for store in stores:

            page_url = "".join(store.xpath(".//@href")).strip()
            if page_url[-1] != "/":
                page_url = page_url + "/"
            if "http" not in page_url:
                page_url = base + page_url
            page_url = page_url.replace("http:", "https:")
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = "".join(store.xpath(".//text()")).strip()
            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[contains(@class,"grid__item") and ./h4]/h4[1]//text()'
                        )
                    ],
                )
            )
            if len(store_info) <= 0:
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[contains(@class,"grid__item") and ./h3]/h3[1]//text()'
                            )
                        ],
                    )
                )
            if not store_info:
                continue

            if len(store_info) == 1:
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[contains(@class,"grid__item") and ./h4]/h4//text()'
                            )
                        ],
                    )
                )
            location_name = store_info[0].strip()

            phone = "<MISSING>"
            for phn_idx, x in enumerate(store_info):
                if bool(re.search("^[0-9-.() ]{1,17}$", x)):
                    break
            if re.search("^[0-9-.() ]{1,17}$", store_info[phn_idx]):
                phone = store_info[phn_idx].strip()
                full_address = store_info[:phn_idx] + store_info[phn_idx + 1 :]
            else:
                phone = "<MISSING>"
                full_address = store_info

            raw_address = " ".join(full_address[1:])

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"
            if zip and " " in zip:
                country_code = "CA"

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[contains(@class,"grid__item") and ./h4]/p//text()'
                        )
                    ],
                )
            )

            if "currently closed" in "; ".join(hours):
                location_type = "Temporarily Closed"

            hours = list(filter(validhour, hours))
            hours_of_operation = (
                " ".join(hours).strip().replace("until further notice:", "").strip()
            )

            map_link = "".join(store_sel.xpath('//a[contains(@href,"maps")]/@href'))
            latitude, longitude = get_latlng(map_link)
            raw_address = "<MISSING>"

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
