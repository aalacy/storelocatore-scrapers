# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import lxml.html
import time

website = "knightfrank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.knightfrank.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.knightfrank.com/contact/offices/atoz"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        countries_req = session.get(
            search_url,
            headers=headers,
        )
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath(
            '//ul[@class="dropdown-menu"]/li[./a[contains(@href,"?country")]]/a/@href'
        )
        for country_url in countries:
            stores_url = search_url + country_url
            log.info(stores_url)
            stores_req = session.get(stores_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//div[@class="atozResults"]/div[./div[contains(@class," office-details")]]/div[contains(@class," office-details")]'
            )
            for store in stores:
                page_url = stores_url
                link = "".join(store.xpath('a[@class="office-link"]/@href')).strip()
                locator_domain = website
                location_name = "".join(
                    store.xpath('*[@class="office-link"]/text()')
                ).strip()

                temp_address = store.xpath("text()")
                add_list = []
                for temp in temp_address:
                    if (
                        len("".join(temp).strip()) > 0
                        and "".join(temp).strip() not in add_list
                    ):
                        add_list.append("".join(temp).strip())

                raw_address = ", ".join(add_list).strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                if state:
                    state = state.replace("Region", "").strip()

                zip = formatted_addr.postcode

                country_code = country_url.split("?country=")[1].strip()

                store_number = "<MISSING>"

                location_type = "<MISSING>"
                phone = "".join(
                    store.xpath('a[contains(@class,"contact-telephone")]/text()')
                ).strip()

                hours_of_operation = "<MISSING>"

                latitude, longitude = "<MISSING>", "<MISSING>"

                if location_name == "Esher":
                    zip = "KT10 9RL"

                if location_name == "International Occupier Services - USA":
                    zip = "W1U 8EW"

                if "/contact/" in link:
                    page_url = link
                    log.info(page_url)
                    try:
                        store_req = SgRequests.raise_on_err(
                            session.get(page_url, headers=headers)
                        )
                        while "captchaPage" in store_req.text:
                            store_req = SgRequests.raise_on_err(
                                session.get(page_url, headers=headers)
                            )
                            time.sleep(3)

                        store_sel = lxml.html.fromstring(store_req.text)
                        map_link = "".join(
                            store_sel.xpath(
                                '//a[@id="cpMain_UserControlContainer12_ctl00_hlDirections"]/@href'
                            )
                        ).strip()
                        log.info(map_link)
                        if len(map_link) <= 0:
                            map_link = "".join(
                                store_sel.xpath('//a[@class="directions"]/@href')
                            ).strip()

                            log.info(map_link)
                        try:
                            latitude = (
                                map_link.split("/")[-1].strip().split(",")[0].strip()
                            )
                        except:
                            pass

                        try:
                            longitude = (
                                map_link.split("/")[-1].strip().split(",")[-1].strip()
                            )
                        except:
                            pass

                        hours = store_sel.xpath(
                            '//div[contains(@class,"office-hours")]/text()'
                        )
                        hours_list = []
                        for hour in hours:
                            if len("".join(hour).strip()) > 0:
                                hours_list.append("".join(hour).strip())

                        hours_temp = (
                            "; ".join(hours_list)
                            .strip()
                            .replace("\r\n", "")
                            .strip()
                            .replace("\n", "")
                            .strip()
                            .replace("\t", "")
                            .strip()
                            .replace("day", "day:")
                            .strip()
                            .replace("::", ":")
                            .strip()
                            .split("; Bank Holiday")[0]
                            .strip()
                        )
                        temp_hours = hours_temp.split(";")
                        hours_list = []
                        if len(temp_hours) > 1:
                            for t in temp_hours:
                                day = t.split("day:")[0].strip() + "day:"
                                tim = t.split("day:")[1].strip()
                                hours_list.append(day + tim)

                        hours_of_operation = "; ".join(hours_list).strip()

                    except SgRequestError as e:
                        log.error(e.status_code)

                if (
                    len(
                        "".join(raw_address)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "")
                        .strip()
                    )
                    <= 0
                ):
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
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
