# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time

from sgrequests import SgRequests


website = "canadagoose.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
cookies = {
    "dwac_bdbM6iaaioAiEaaaddLOa2751H": "5zBSqqCgqo-Qh-OsGqJD8SPGUApy0D0WdcI%3D|dw-only|||CAD|false|Canada%2FEastern|true",
    "cquid": "||",
    "sid": "5zBSqqCgqo-Qh-OsGqJD8SPGUApy0D0WdcI",
    "dwanonymous_4b678b2f3ddcd887e7cd4635d93160c7": "abNegpNMspKSMAXtWu1W8QeTJk",
    "dwsid": "IXwvsbBsWscXjqebqaYW9-WKLRFiHM1e8ssk9-slJfCbIH7VKgANBcmcMkaSLyHBEuIYOQWJiIKtmYeAhPJMKA==",
    "__cq_dnt": "0",
    "dw_dnt": "0",
    "zarget_visitor_info": "%7B%7D",
    "zarget_user_id": "10362e94-7e5b-4da3-d0fc-0990bca3e920",
    "dw": "1",
    "dw_cookies_accepted": "1",
    "BVImplmain_site": "14687",
    "CanadaGooseCA-pagevisits": '{"pagevisits":1}',
    "globalBannerIsHidden": "",
    "_f60_session": "F51bc4RMEMlniAacispQfGvClyxfgaZZ1oqzsh2DwoKMWnxGSiumFe7Z9ggea7GZ",
    "_gcl_au": "1.1.287433129.1635279167",
    "rskxRunCookie": "0",
    "rCookie": "vcvnl862xnd9q6xvm4c1kv8izv6a",
    "_ga": "GA1.2.1616322722.1635279171",
    "_gid": "GA1.2.418098902.1635279171",
    "_gat_UA-34770126-1": "1",
    "_li_dcdm_c": ".canadagoose.com",
    "_lc2_fpi": "c88e71b6d53c--01fjz3qv2x2rfydykm9qcezzef",
    "__cq_uuid": "abNegpNMspKSMAXtWu1W8QeTJk",
    "__cq_seg": "0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00",
    "BVBRANDID": "55d9849f-a61c-4407-b3ea-91360d48c72c",
    "BVBRANDSID": "396a7e4a-cc2e-4633-95bb-9ae707036309",
    "_pin_unauth": "dWlkPU5XRTJORGcwWmpRdFlXSXdNaTAwTjJNNExUazJZVEl0WldRMU1XSTBZMk5qTjJZMQ",
    "dwac_cdSAUiaaio11EaaadnOiJrNbA7": "5zBSqqCgqo-Qh-OsGqJD8SPGUApy0D0WdcI%3D|dw-only|||USD|false|Canada%2FEastern|true",
    "cqcid": "adeIw7sb8AQap4aaDLC4pOeWWN",
    "dwanonymous_b3aa5771d8435c67a1a8775183c875b2": "adeIw7sb8AQap4aaDLC4pOeWWN",
    "language": "en",
    "countryCode": "US",
    "CanadaGooseUS-pagevisits": '{"pagevisits":1}',
    "_uetsid": "185e9b90369911ec989b29d7ef1b1637",
    "_uetvid": "185ef410369911ec8d92b156bb706a4f",
    "_scid": "823065e7-6be4-4e21-87d0-53d9d89f0897",
    "akm_bmfp_b2-ssn": "0Ip7AXK8K2KG6vLuDU7vuBnpfcmeXblFAQztnaXvWehNSgNH2BuR6irrvLnCgn5PrvnRfhWIsFoGBPYDbSMzL2fdlptSyrvF6HKqF9iQAdzXhUtyuflV0RRaapXTONuIZxVxkbDGxzWrYxDJB0rhKnHeb",
    "akm_bmfp_b2": "0Ip7AXK8K2KG6vLuDU7vuBnpfcmeXblFAQztnaXvWehNSgNH2BuR6irrvLnCgn5PrvnRfhWIsFoGBPYDbSMzL2fdlptSyrvF6HKqF9iQAdzXhUtyuflV0RRaapXTONuIZxVxkbDGxzWrYxDJB0rhKnHeb",
    "civicCookieControl": "%7B%22pv%22%3A%22%22%2C%22cm%22%3A%22info%22%2C%22open%22%3A%22no%22%2C%22consented%22%3A%22yes%22%2C%22explicitly%22%3A%22yes%22%2C%22hidden%22%3A%22yes%22%7D",
    "lastRskxRun": "1635279182908",
}


headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
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
    search_url = (
        "https://www.canadagoose.com/us/en/find-a-retailer/find-a-retailer.html"
    )

    with SgRequests(
        proxy_country="us",
        dont_retry_status_codes=([404]),
        retries_with_fresh_proxy_ip=20,
    ) as session:
        response = session.get(search_url, headers=headers, cookies=cookies)
        search_sel = lxml.html.fromstring(response.text, "lxml")
        store_list = search_sel.xpath('//div[@class="store"]')
        log.info(f"Total Locations to crawl: {len(store_list)}")
        for store in store_list:

            page_url = store.xpath("./a/@href")[0].strip()
            log.info(f"Now crawling: {page_url}")
            response2 = session.get(page_url, headers=headers)
            time.sleep(3)
            store_sel = lxml.html.fromstring(response2.text, "lxml")

            locator_domain = website

            street_address = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="streetAddress"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            city = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="addressLocality"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            try:
                if city[-1] == ",":
                    city = "".join(city[:-1]).strip()
            except:
                city = "<MISSING>"

            state = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="addressRegion"]//text()'
                )
            ).strip()
            zip = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="postalCode"]//text()'
                )
            ).strip()

            if len(street_address) <= 0:
                street_address = ", ".join(
                    "".join(
                        store_sel.xpath(
                            '//div[@class="store-info desktop"]//*[@itemprop="address"]//text()'
                        )
                    )
                    .strip()
                    .split(",")[:-1]
                ).strip()

            country_code = "<INACCESSIBLE>"
            if "Italy" == state:
                country_code = "IT"
                state = "<MISSING>"
            if "France" == state:
                country_code = "FR"
                state = "<MISSING>"
            if "Taiwan" == state:
                country_code = "TW"
                state = "<MISSING>"

            try:
                if state.split(" ")[0].strip().isdigit():
                    zip = state.split(" ", 1)[0].strip()
                    state = state.split(" ", 1)[-1].strip()
            except:
                pass
            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//span[@itemprop="name"]/text()'
                )
            ).strip()

            phone = store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="telephone"]//text()'
            )
            if len(phone) > 0:
                phone = "".join(phone[0]).strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours = store_sel.xpath('//div[@class="store-info desktop"]/text()')
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            if len(hours_list) <= 0:
                hours = store_sel.xpath(
                    '//div[@class="store-info desktop"]/p[./meta[@itemprop="openingHours"]]/text()'
                )
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

            if len(hours_list) <= 0:
                hours = store_sel.xpath('//div[@class="store-info desktop"]/p/text()')
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

            hours_of_operation = "; ".join(hours_list).strip()
            if "," == hours_of_operation:
                hours_of_operation = "<MISSING>"

            map_link = "".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//a[contains(@href,"maps")]/@href'
                )
            )

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
