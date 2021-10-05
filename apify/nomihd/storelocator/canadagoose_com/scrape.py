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
session = SgRequests()

cookies = {
    "dwanonymous_b3aa5771d8435c67a1a8775183c875b2": "adt8yYpartGjBT4acGDvbA75LT",
    "BVBRANDID": "f333f2c0-e7bf-4191-b38b-22502fcde1ef",
    "dwanonymous_2954ea0b586e0f3a1c58971e98526cb1": "beH9ZjJyHc2aAyIXhV5wms3wbr",
    "dwanonymous_4b678b2f3ddcd887e7cd4635d93160c7": "deEhWuRbc41unMaWN624yxAdge",
    "_scid": "593cc78b-eedb-4eab-8165-f722d3c391bf",
    "dwac_cdSAUiaaio11EaaadnOiJrNbA7": "rIiNnax-qkk5eNK2Jvc0j1RFtNOG8JG7RxI%3D|dw-only|||USD|false|Canada%2FEastern|true",
    "cquid": "||",
    "__cq_dnt": "0",
    "dw_dnt": "0",
    "zarget_visitor_info": "%7B%7D",
    "zarget_user_id": "2f0dde7c-585c-4579-b996-ac4b1b998e7a",
    "_gcl_au": "1.1.860488317.1633360934",
    "_ga": "GA1.2.887594067.1633360936",
    "_gid": "GA1.2.1920819951.1633360936",
    "_li_dcdm_c": ".canadagoose.com",
    "_lc2_fpi": "c88e71b6d53c--01fh5yc0hwt99pzx9yrmp6yqjc",
    "dw": "1",
    "dw_cookies_accepted": "1",
    "BVImplmain_site": "14687",
    "globalBannerIsHidden": "",
    "_pin_unauth": "dWlkPU5EaG1NelUzT0RFdE1XRmpPUzAwT1RBeUxXSTJaV1V0TmpaaFpEVmhNV1V4TlRReQ",
    "__cq_uuid": "absHmGtKqd2YWuvTkgqrGzqkFq",
    "__cq_seg": "0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00",
    "rskxRunCookie": "0",
    "rCookie": "5u0tvyvfe86ccefhqrcbrokucsxq3m",
    "civicCookieControl": "%7B%22pv%22%3A%22%22%2C%22cm%22%3A%22info%22%2C%22open%22%3A%22no%22%2C%22consented%22%3A%22yes%22%2C%22explicitly%22%3A%22yes%22%2C%22hidden%22%3A%22yes%22%7D",
    "contactWindowDialogIsHidden": "1",
    "CanadaGooseUS-pagevisits": '{"pagevisits":5}',
    "_sctr": "1|1633287600000",
    "cqcid": "deEhWuRbc41unMaWN624yxAdge",
    "_derived_epik": "dj0yJnU9OTRuVUdVeGFMNnN0WHVfOHdmMHFBSnRRUGxrZUFPX0gmbj1JR0hseXVjRzJpd2ZKa3ppSUZxamVnJm09ZiZ0PUFBQUFBR0ZiSUJvJnJtPWYmcnQ9QUFBQUFHRmJJQm8",
    "_f60_session": "F51hqZiTYbk4PIg16hnwMXH32whiHfkmFi2OCwZlnluC9maJDeh8fw29PvwFUmgB",
    "countryCode": "CA",
    "CanadaGooseCA-pagevisits": '{"pagevisits":1}',
    "_uetsid": "dd254c80252611ec9a229fec4359ef9e",
    "_uetvid": "4c9bf690e62511eb977165ee7ae05647",
    "lastRskxRun": "1633361953500",
    "dwac_bdbM6iaaioAiEaaaddLOa2751H": "LT4AGzBxpt35rCSzCwRu_vKgGnxE399yCZc%3D|dw-only|||CAD|false|Canada%2FEastern|true",
    "sid": "LT4AGzBxpt35rCSzCwRu_vKgGnxE399yCZc",
    "language": "en_CA",
    "dwsid": "CV6wuXX08AjG5BkBfAKdY9bAqt4BWomnNt84yUd2psq3sR6Kh_yInxn8k3YgRardxdQJlxOEO0si4E2It5zmiw==",
    "akm_bmfp_b2-ssn": "0yrCqdR2fcUnHY7H2isgsUjwQ3dhyUVmWm0UPGcT5tSSlZySAacYEwshCGz0paeaRN1HAt60Sc8LbTAxoBQZBVZuKcegDM2OsS3wy3K77TzTA4E1MyzOF4QZHAarCuotAzZGTTLw6DafZu4kF4TI2IwaJ",
    "akm_bmfp_b2": "0yrCqdR2fcUnHY7H2isgsUjwQ3dhyUVmWm0UPGcT5tSSlZySAacYEwshCGz0paeaRN1HAt60Sc8LbTAxoBQZBVZuKcegDM2OsS3wy3K77TzTA4E1MyzOF4QZHAarCuotAzZGTTLw6DafZu4kF4TI2IwaJ",
    "_gat_UA-34770126-1": "1",
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
        country_code = "<INACCESSIBLE>"

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

        hours_of_operation = "; ".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="openingHours"]/@content'
            )
        ).strip()
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
