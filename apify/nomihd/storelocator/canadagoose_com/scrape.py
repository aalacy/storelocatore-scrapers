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

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": 'dwac_bdbM6iaaioAiEaaaddLOa2751H=_8ItzVhV3QBbbsGixlyFTBbpWQNB700pSQQ%3D|dw-only|||CAD|false|Canada%2FEastern|true; cqcid=bfbsaKiqHEBqXUAqEYsdVqc5nE; cquid=||; sid=_8ItzVhV3QBbbsGixlyFTBbpWQNB700pSQQ; dwanonymous_4b678b2f3ddcd887e7cd4635d93160c7=bfbsaKiqHEBqXUAqEYsdVqc5nE; dwsid=qrgFgg-oB9aUHXbdPPCvyUOTcUwWEpf_hnexrzMBC8r5ZbMBzh8XM5IPuIdoBVEyFIPSH103jxP8SW9WIshRYw==; language=en; __cq_dnt=0; dw_dnt=0; zarget_visitor_info=%7B%7D; zarget_user_id=f4bdfdfd-3d02-4caa-aa4f-4da851eff142; _gcl_au=1.1.850673134.1633361980; _f60_session=F51XbzGNvDgDQ9ujiTUyBZEXgjBleIScywMRAip7wl5N2U7LYixNhaWwpi27znCV; _ga=GA1.2.2128220691.1633361982; _gid=GA1.2.1574803012.1633361982; _li_dcdm_c=.canadagoose.com; _lc2_fpi=c88e71b6d53c--01fh5zbwfcpb8wqnn7b3w5wgf1; _pin_unauth=dWlkPVpUQTJPRFJoTURZdFpEbGpaQzAwTmpoa0xUazRPREV0TWpFMFpXTTVNalUwT1RNeA; dw=1; dw_cookies_accepted=1; BVImplmain_site=14687; countryCode=CA; CanadaGooseCA-pagevisits={"pagevisits":1}; globalBannerIsHidden=; _uetsid=4d1e6300252911eca361edacbd241f06; _uetvid=4d1eeab0252911ecb332b763d30a428c; BVBRANDID=3b15c22d-8977-463b-9812-3ca4f8a71490; BVBRANDSID=7af54421-8a53-48b6-b6be-077ab7e4e3e8; __cq_uuid=bfbsaKiqHEBqXUAqEYsdVqc5nE; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; rskxRunCookie=0; rCookie=rs62kn30ncgnj6uuqpphtkuctjzyo; lastRskxRun=1633361990507; akm_bmfp_b2-ssn=0SwZK0SFPjIOZ1edzMVB4UvDv3Vo8CmPnjG9it1VLaMKNmq6Jaf5vKAgrCMWvLz21lBzBguk3dGcBUui0jHmBI3I8z3YSNoYLWMnBwiSvaOb4ZTij3ZVypCnY7aAHGJIMUJUh9FurGxygPE3V0RdObUg7; akm_bmfp_b2=0SwZK0SFPjIOZ1edzMVB4UvDv3Vo8CmPnjG9it1VLaMKNmq6Jaf5vKAgrCMWvLz21lBzBguk3dGcBUui0jHmBI3I8z3YSNoYLWMnBwiSvaOb4ZTij3ZVypCnY7aAHGJIMUJUh9FurGxygPE3V0RdObUg7',
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

    response = session.get(search_url, headers=headers)
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
