# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "fiat.com.uy"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
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
    elif "&q=" in map_link:
        latitude = map_link.split("&q=")[1].split(",")[0].strip()
        longitude = map_link.split("&q=")[1].split(",")[1].strip()
    elif "?q=" in map_link:
        latitude = map_link.split("?q=")[1].split(",")[0].strip()
        longitude = map_link.split("?q=")[1].split(",")[1].strip().split("&")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    urls_list = [
        "https://www.fiat.com.pe/propietarios/concesionarios/",
        "https://www.fiat.com.py/propietarios/concesionarios/",
        "https://www.fiat.com.uy/propietarios/concesionarios/",
        "https://www.fiat.cr/propietarios/sucursales/",
        "https://www.fiatbolivia.bo/propietarios/concesionarios/",
    ]
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        for search_url in urls_list:
            log.info(search_url)
            search_res = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(search_res.text)
            cities_dict = {}
            cities = stores_sel.xpath('//select[@id="c2"]/option[position()>1]')
            for city in cities:
                cities_dict["".join(city.xpath("@value")).strip()] = "".join(
                    city.xpath("@data-region")
                ).strip()
            stores = stores_sel.xpath("//div[@data-comuna]")
            for store in stores:
                if len("".join(store.xpath("@data-comuna")).strip()) <= 0:
                    continue
                page_url = search_url
                locator_domain = website
                location_name = "".join(store.xpath("div[1]//h4/text()")).strip()

                temp_address = store.xpath("div[1]//p[1]/text()")
                add_list = []
                for temp in temp_address:
                    if (
                        len("".join(temp).strip()) > 0
                        and "@" not in "".join(temp).strip()
                    ):
                        add_list.append("".join(temp).strip())

                raw_address = ", ".join(add_list).strip()
                phone = "".join(
                    store.xpath('div[2]/div[1]/div[@class="telefono"]/text()')
                ).strip()
                if "Tel." in raw_address:
                    raw_address = raw_address.split("Tel.")[0].strip()
                    if len(phone) <= 0:
                        phone = (
                            raw_address.split("Tel.")[1].strip().split("|")[0].strip()
                        )

                if raw_address:
                    raw_address = (
                        raw_address.replace("\r\n", "")
                        .strip()
                        .replace("\n", "")
                        .strip()
                        .replace("\r", "")
                        .strip()
                    )
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = "".join(store.xpath("@data-comuna")).strip()
                if city not in cities_dict:
                    if city == "v-valparaiso":
                        city = "valparaiso"

                state = cities_dict[city]
                if "-" in state:
                    state = state.split("-", 1)[-1].strip()

                zip = formatted_addr.postcode

                country_code = (
                    search_url.split("/propietarios")[0].strip().split(".")[-1].strip()
                )

                store_number = "<MISSING>"
                location_type = "<MISSING>"

                hours_list = []
                days = store.xpath('div[2]/div[1]/div[@class="tit-day"]')
                time = store.xpath('div[2]/div[1]/div[@class="h-day"]')
                days_list = []
                time_list = []
                for day in days:
                    days_list.append("".join(day.xpath("text()")).strip())

                for tim in time:
                    if len("".join(tim.xpath("span/text()")).strip()) <= 0:
                        time_list.append("not_available")
                    else:
                        time_list.append("".join(tim.xpath("span/text()")).strip())

                for index in range(0, len(days_list)):
                    if time_list[index] != "not_available":
                        hours_list.append(days_list[index] + ":" + time_list[index])

                hours_of_operation = "".join(hours_list).strip()
                map_link = "".join(
                    store.xpath('.//a[contains(text(),"Google Maps")]/@href')
                ).strip()
                latitude, longitude = get_latlng(map_link)
                phone = (
                    phone.split("/")[0]
                    .strip()
                    .split(" - ")[0]
                    .strip()
                    .lower()
                    .split("anexo")[0]
                    .strip()
                )
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
