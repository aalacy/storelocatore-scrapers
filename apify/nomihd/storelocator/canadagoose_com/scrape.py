# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from sgselenium import SgChrome
from selenium.webdriver.chrome.options import Options

website = "canadagoose.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
cookies = {
    "dwac_bdbM6iaaioAiEaaaddLOa2751H": "1E8J2BU68uM7MlzPcXysavEVvtjty8yRz2w%3D|dw-only|||CAD|false|Canada%2FEastern|true",
    "cqcid": "bcnik6hrim0a2QsVSYgoEz8eAR",
    "cquid": "||",
    "sid": "1E8J2BU68uM7MlzPcXysavEVvtjty8yRz2w",
    "dwanonymous_4b678b2f3ddcd887e7cd4635d93160c7": "bshould becnik6hrim0a2QsVSYgoEz8eAR",
    "dwsid": "UNcLmxlzu67CTw9L24EOaPKW3gS6w_Tu9p0bRXrN1mvQHoomoxclvfeJ10CFUJB0WemOKarPtKXt6f_ok3dLqQ==",
    "language": "en_CA",
    "__cq_dnt": "0",
    "dw_dnt": "0",
    "zarget_visitor_info": "%7B%7D",
    "zarget_user_id": "8fa7a974-9026-4c77-cccb-c67993019082",
    "dw": "1",
    "dw_cookies_accepted": "1",
    "BVImplmain_site": "14687",
    "countryCode": "CA",
    "globalBannerIsHidden": "",
    "_gcl_au": "1.1.1818709287.1635334860",
    "_f60_session": "F51zHuuWu33nlb0oklaP0M9HiT8gbkVA2RoyWK3ZlB66CJPA4nCuaocJ3tMYjKf6",
    "rskxRunCookie": "0",
    "rCookie": "j6txeehph1gkz908pwa9akv9g5is3",
    "_ga": "GA1.2.919671090.1635334862",
    "_gid": "GA1.2.1146887470.1635334862",
    "_gat_UA-34770126-1": "1",
    "_li_dcdm_c": ".canadagoose.com",
    "_lc2_fpi": "c88e71b6d53c--01fk0rvcyccp91jcw9f7e0v5k4",
    "__cq_uuid": "bcnik6hrim0a2QsVSYgoEz8eAR",
    "__cq_seg": "0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00",
    "BVBRANDSID": "acfd3e97-15a2-4919-a73a-00a1d78037f6",
    "BVBRANDID": "4f4fa95b-2525-4639-b0ed-61b54f231dad",
    "_pin_unauth": "dWlkPVpEWXpaVEkxTW1FdFlqZG1OeTAwWXpsakxXSTROelF0TmpWaVlXSTJZVEV5WVdOaA",
    "CanadaGooseCA-pagevisits": '{"pagevisits":2}',
    "_uetsid": "c2dfd030371a11ec8bdd99b3509bbb58",
    "_uetvid": "c2e04fa0371a11ec9dd46303d2152595",
    "lastRskxRun": "1635334896569",
    "akm_bmfp_b2-ssn": "09hUmpWjaolpzQaAEd24fOp3nEHJqYPAfN5tMTxd0u0CxY7WfcUcVKBi8j6poxGaKJUsdpT295MrYMKa81KNI0ZUT848PpBNnJEnPfvUeZWqXO3xcYxfsSjK9v43qrC09aiMRGU078mUUp9fnSgYOgbc",
    "akm_bmfp_b2": "09hUmpWjaolpzQaAEd24fOp3nEHJqYPAfN5tMTxd0u0CxY7WfcUcVKBi8j6poxGaKJUsdpT295MrYMKa81KNI0ZUT848PpBNnJEnPfvUeZWqXO3xcYxfsSjK9v43qrC09aiMRGU078mUUp9fnSgYOgbc",
}


headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.canadagoose.com/",
    "Accept-Language": "en-US,en;q=0.9",
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
    search_url = "http://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"

    chrome_options = Options()
    chrome_options.accept_untrusted_certs = True
    chrome_options.assume_untrusted_cert_issuer = True
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--allow-http-screen-capture")
    chrome_options.add_argument("--disable-impl-side-painting")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-seccomp-filter-sandbox")

    with SgChrome(
        is_headless=True,
        chrome_options=chrome_options,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    ) as session:
        session.get(search_url)
        log.info(session.page_source)
        search_sel = lxml.html.fromstring(session.page_source, "lxml")
        store_list = search_sel.xpath('//div[@class="store"]')
        log.info(f"Total Locations to crawl: {len(store_list)}")
        for store in store_list:

            page_url = store.xpath("./a/@href")[0].strip()
            log.info(f"Now crawling: {page_url}")
            session.get(page_url)
            time.sleep(3)
            store_sel = lxml.html.fromstring(session.page_source, "lxml")

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
