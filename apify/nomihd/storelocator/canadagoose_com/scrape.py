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
    "Cookie": 'dwac_cdSAUiaaio11EaaadnOiJrNbA7=H8_H7RgIcfzRZ2cE6KGWLq_2XwME0CGNAm8%3D|dw-only|||USD|false|Canada%2FEastern|true; cquid=||; sid=H8_H7RgIcfzRZ2cE6KGWLq_2XwME0CGNAm8; language=en; dwanonymous_b3aa5771d8435c67a1a8775183c875b2=cd4goGJXMb3zbrbNp8a9XB7Nop; dwsid=2EHgyYmjZHvyRRGZhGiJLGh4eCeVezQKIU1tbc_wjeX7hc2A3RNEvEIGMduRH6BxlEYW8qXRcx9manJ-CSEmYQ==; __cq_dnt=0; dw_dnt=0; zarget_visitor_info=%7B%7D; zarget_user_id=20f35c11-53a1-4921-9445-7ad3031f75e8; dw=1; dw_cookies_accepted=1; BVImplmain_site=14687; globalBannerIsHidden=; __cq_uuid=ab0kwZSrU5LjRDfnQ14RitBNF9; __cq_seg=0~0.00u00211~0.00u00212~0.00u00213~0.00u00214~0.00u00215~0.00u00216~0.00u00217~0.00u00218~0.00u00219~0.00; _gcl_au=1.1.1696010982.1633246797; BVBRANDID=b41a54ab-b5cf-4e49-a68d-a03f0f707312; _ga=GA1.2.23858703.1633246798; _gid=GA1.2.108630905.1633246798; _li_dcdm_c=.canadagoose.com; _lc2_fpi=c88e71b6d53c--01fh2hgr6r35se2nt9cmzetx2d; _fbp=fb.1.1633246798768.103846891; _pin_unauth=dWlkPVpUQmxaR1JrT1RJdE16WTBNQzAwTTJFMkxUbG1aR1V0WWpsaU0ySXpaV1ppWldWaw; rskxRunCookie=0; rCookie=ml8ljtt2vpl2at8hi1l4tmkuawz9j6; civicCookieControl=%7B%22pv%22%3A%22%22%2C%22cm%22%3A%22info%22%2C%22open%22%3A%22no%22%7D; CanadaGooseUS-pagevisits={"pagevisits":3}; BVBRANDSID=afd14d06-50c3-4a76-9777-274de8f3ed51; dwac_bdbM6iaaioAiEaaaddLOa2751H=H8_H7RgIcfzRZ2cE6KGWLq_2XwME0CGNAm8%3D|dw-only|||CAD|false|Canada%2FEastern|true; cqcid=adegnkhaTBst7h7ZLU0b7qgO5r; dwanonymous_4b678b2f3ddcd887e7cd4635d93160c7=adegnkhaTBst7h7ZLU0b7qgO5r; countryCode=CA; _f60_session=F51GHj1laVAs50apMRbA92P5Y3AfnXadrRXSzWxYKZberTuDAgfwHcMcYvmIEMyH; _gat_UA-34770126-1=1; CanadaGooseCA-pagevisits={"pagevisits":4}; _uetsid=1bfb1a10241d11eca0c317f624160b29; _uetvid=1bfb4370241d11ec99fde1a140434de5; lastRskxRun=1633256485695; akm_bmfp_b2-ssn=0w0mkiHDtQPuInX54XuMvOSIFFW40I5CHJivgFai2Ijvorf0qtfwBl0Ls76bqQUH2UxxxPIaaBF42QlcQGsVrZq9alNZRIff8OyyZdTGhKn1LYtP6WBUL3J5WPzBmAgLwseXnCyyaLcsywf5SUD4ilta1; akm_bmfp_b2=0w0mkiHDtQPuInX54XuMvOSIFFW40I5CHJivgFai2Ijvorf0qtfwBl0Ls76bqQUH2UxxxPIaaBF42QlcQGsVrZq9alNZRIff8OyyZdTGhKn1LYtP6WBUL3J5WPzBmAgLwseXnCyyaLcsywf5SUD4ilta1; __cq_dnt=0; dw_dnt=0; akm_bmfp_b2-ssn=0Qpi37YlIPWjWceHAOQl2tA9RCgqqGGuqqYzE1sFM4Ha9ikFRGCBeZkhum1P1EUvSa5LDBVMelqgzH4ZY8xnLMcgKdyDnASXwhkCMzZt0t9I2zz4ed2BYI9NKePbwJAtcRCA4gvW7yTTHWVGipsCcu52W; akm_bmfp_b2=0Qpi37YlIPWjWceHAOQl2tA9RCgqqGGuqqYzE1sFM4Ha9ikFRGCBeZkhum1P1EUvSa5LDBVMelqgzH4ZY8xnLMcgKdyDnASXwhkCMzZt0t9I2zz4ed2BYI9NKePbwJAtcRCA4gvW7yTTHWVGipsCcu52W',
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
        country_code = "CA"

        location_name = "".join(
            store_sel.xpath('//div[@class="store-info desktop"]//h3[last()]/text()')
        ).strip()

        phone = " ".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="telephone"]//text()'
            )
        ).strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "; ".join(
            store_sel.xpath(
                '//div[@class="store-info desktop"]//*[@itemprop="openingHours"]//text()'
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
