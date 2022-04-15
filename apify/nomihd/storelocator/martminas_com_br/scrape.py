# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "martminas.com.br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Origin": "https://martminas.com.br",
    "Referer": "",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

data = {
    "form_build_id": "form-7W0QQzBugB7pRGMgfsPwkB8AV4pJvER8anEnWRtgdbw",
    "form_id": "global_filter_1",
    "field_cidade": "242",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://martminas.com.br/lojas"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        form_build_id = "".join(
            search_sel.xpath(
                '//div[@class="localizacao"]//form[@id="global-filter-1"]//input[@name="form_build_id"]/@value'
            )
        )

        stores = search_sel.xpath(
            '//div[@class="localizacao"]//form[@id="global-filter-1"]//option'
        )

        headers["Referer"] = search_url
        for store in stores:

            locator_domain = website

            page_url = search_url
            data["form_build_id"] = form_build_id
            field_cidade = "".join(store.xpath("./@value")).strip()
            if not field_cidade:
                continue
            data["field_cidade"] = field_cidade

            log.info(data)
            store_res = session.post(search_url, headers=headers, data=data)
            log.info(store_res)

            store_sel = lxml.html.fromstring(store_res.text)
            form_build_id = "".join(
                store_sel.xpath(
                    '//div[@class="localizacao"]//form[@id="global-filter-1"]//input[@name="form_build_id"]/@value'
                )
            )

            location_name = "".join(
                store_sel.xpath('//div[@class="info-local"]//h1//text()')
            ).strip()
            log.info(location_name)
            if not location_name:
                continue

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="info-local"]//p//text()'
                        )
                    ],
                )
            )

            raw_address = " ".join(store_info).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city
            if not city:
                city = store_info[-1].strip()

            state = formatted_addr.state
            zip = formatted_addr.postcode
            if not zip:
                zip = store_info[-2].strip().replace("CEP:", "").strip()

            country_code = "BR"

            store_number = field_cidade
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="info-local"]//following::div[@class="telefone"]//li[1]//text()'
                )
            )

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="info-local"]//following::div[@class="horarios"]//li//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours)
                .replace("Dom;", "Dom:")
                .replace("b;", "b:")
                .replace("Dia:; ", "")
                .replace("Hora:; ", "")
                .strip()
            )
            map_link = "".join(store_sel.xpath('//iframe[contains(@src,"maps")]/@src'))

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
