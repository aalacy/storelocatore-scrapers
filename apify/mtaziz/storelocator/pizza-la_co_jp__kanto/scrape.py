# -*- coding: utf-8 -*-
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
from lxml import html


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MAX_WORKERS = 3

logger = SgLogSetup().get_logger(logger_name="pizza-la_co_jp__kanto")

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "www.pizza-la.co.jp",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}

STORE_LOCATOR = "https://www.pizza-la.co.jp/TenpoTop.aspx"
BASE_URL = "https://www.pizza-la.co.jp/"


# URL Depth Level 1


def get_level1_store_locator_urls():
    with SgRequests(
        proxy_country="gb",
    ) as http:
        # https://www.pizza-la.co.jp/paella/TenpoSelect.aspx?KC=01"
        rp = http.get(STORE_LOCATOR, headers=headers)
        logger.info(f"Pulling Content from Store Locator: {STORE_LOCATOR}")
        selp = html.fromstring(rp.text, "lxml")
        xpath = '//a[contains(@href, "TenpoTop.aspx?M=P")]/@href'
        perfecture_level1 = selp.xpath(xpath)
        urls1 = [f"{BASE_URL}{i}" for i in perfecture_level1]
        return urls1


# URL Depth Level 2


def get_level2_store_locator_urls(urls1):
    urls2 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(urls1[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[LEVEL2] PullingStoreLocators: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # Example URL https://www.pizza-la.co.jp/TenpoTop.aspx?M=CK&C=01
            xpath = '//a[contains(@href, "TenpoTop.aspx?M=CK")]/@href'
            slugs2 = selp.xpath(xpath)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"Level2Count: {len(urls)}")
            urls2.extend(urls)
        logger.info(f"Level2Count: {len(urls)}")
        return urls2


# URL Depth Level 3


def get_level3_store_locator_urls(ret_urls2):
    urls3 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(ret_urls2[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[LEVEL3] PullingStoreLocators: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # Response from https://www.pizza-la.co.jp/TenpoTop.aspx?M=CS&C=01&amp;K=あ does not return
            # the stores listed on this page, but in order to make it work,
            # we have to transform あ to %82%A0 that would yield
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=CS&C=01&K=%82%A0 .
            xpath = '//a[contains(@href, "TenpoTop.aspx?M=CS")]/@href'
            slugs2 = selp.xpath(xpath)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"Count: {len(urls)}")
            urls3.extend(urls)

        return urls3


def normalize_the_store_locator_url(urls3):
    normalized_urls4 = []
    for idx, url in enumerate(urls3):
        logger.info(f"To be encoded by cp932: {url}")
        t = url.split("=")[-1]
        t2 = "=".join(url.split("=")[:-1])
        encoded_cp = t.encode("cp932")
        logger.info(f"[{idx}] Encoded as {encoded_cp}")
        decoded_k = (
            str(encoded_cp)
            .lstrip("b")
            .replace("'", "")
            .replace("\\", "%")
            .replace("x", "")
            .upper()
        )
        url_to_be_tested = f"{t2}={decoded_k}"
        # URL must be like https://www.pizza-la.co.jp/TenpoTop.aspx?M=CS&C=10&K=%82%A0
        url_to_be_tested = url_to_be_tested.replace("amp;", "")
        normalized_urls4.append(url_to_be_tested)
    return normalized_urls4


# URL Depth Level 4


def get_level4_store_locator_urls(japanese_k_normalized):
    urls4 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(japanese_k_normalized[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[LEVEL4] PullingStoreLocator: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=TK&C=10204
            xpath = '//a[contains(@href, "TenpoTop.aspx?M=TK")]/@href'
            slugs2 = selp.xpath(xpath)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"Count: {len(urls)}")
            urls4.extend(urls)

        return urls4


# URL Depth Level 5


def get_level5_store_locator_urls(m_tk_c_urls):
    urls5 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(m_tk_c_urls[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[{idx1}][LEVEL5] PullingUrlsFrom: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=TS&C=10204&K=あ needs to be transformed to
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=TS&C=10204&K=%82%A0
            xpath = '//a[contains(@href, "TenpoTop.aspx?M=TS")]/@href'
            slugs2 = selp.xpath(xpath)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"CountAtLevel5: {len(urls)}")
            urls5.extend(urls)

        return urls5


def normalize_level5_the_store_locator_url(MTS_URL):

    # https://www.pizza-la.co.jp/TenpoTop.aspx?M=TS&C=10204&K=%82%A0 URL must be encoded by cp932,
    # otherwise, it won't work.

    normalized_urls5 = []
    for idx, url in enumerate(MTS_URL):
        jp_letters = url.split("=")[-1]
        jp_url_part_1 = "=".join(url.split("=")[:-1])

        logger.info(f"jp_url_part1: {jp_url_part_1}")
        encoded_cp = jp_letters.encode("cp932")
        logger.info(f"Encoded as: {encoded_cp}")
        decoded_k = (
            str(encoded_cp)
            .lstrip("b")
            .replace("'", "")
            .replace("\\", "%")
            .replace("x", "")
            .upper()
        )
        url_formed = f"{jp_url_part_1}={decoded_k}"
        url_formed = url_formed.replace("amp;", "")
        logger.info(f"URLFormed: {url_formed}")
        normalized_urls5.append(url_formed)
    logger.info(f"Normalized Level 5: {normalized_urls5}")
    return normalized_urls5


# URL Depth Level 6-1


def get_level61_store_urls(m_tk_c_urls):
    urls61 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(m_tk_c_urls[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[LEVEL61] PullingStoreLocator: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=AS&C=10204006
            xpath = '//a[contains(@href, "Tenpo.aspx?M=TS")]/@href'
            slugs2 = selp.xpath(xpath)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"Count: {len(urls)}")
            urls61.extend(urls)
    return urls61


# URL Depth Level 6


def get_level6_store_urls(urls_11digits_id):
    urls6 = []
    with SgRequests(
        proxy_country="gb",
    ) as http:
        for idx1, url1 in enumerate(urls_11digits_id[0:]):
            rp = http.get(url1, headers=headers)
            logger.info(f"[LEVEL6] PullingStoreUrls: {url1}")
            selp = html.fromstring(rp.text, "lxml")
            # After encoding あ using cp932, we get %82%A0.
            # See normalize functions above
            # Store URL Example
            # https://www.pizza-la.co.jp/Tenpo.aspx?M=TS&C=10204081000&B=M%3dTS%26C%3d10204%26K%3d%25u3042
            # Store URL contains multiple stores
            # https://www.pizza-la.co.jp/TenpoTop.aspx?M=AS&C=10204088
            xpath_mts = '//a[contains(@href, "Tenpo.aspx?M=TS")]/@href'
            slugs2 = selp.xpath(xpath_mts)
            urls = [f"{BASE_URL}{i}" for i in slugs2]
            logger.info(f"Level6 Count: {len(urls)}")
            xpath_mas_multi_store = '//a[contains(@href, "TenpoTop.aspx?M=AS")]/@href'
            slugs_multi = selp.xpath(xpath_mas_multi_store)
            urls_multi = [f"{BASE_URL}{i}" for i in slugs_multi]
            logger.info(f"{urls_multi} Contains Multi-stores")
            urls_level61 = get_level61_store_urls(urls_multi)
            logger.info(f"Level61 Count: {len(urls_level61)}")
            urls.extend(urls_level61)
            urls6.extend(urls)
    return urls6


def fetch_records(idx, page_url, sgw: SgWriter):
    with SgRequests() as session:
        store_res = session.get(page_url, headers=headers)
        store_sel = html.fromstring(store_res.text)

        location_name = " ".join(
            store_sel.xpath('//h1[@class="title"]//text()')
        ).strip()

        store_info = list(
            filter(
                str,
                [x.strip() for x in store_sel.xpath("//table//tr[last()]/td//text()")],
            )
        )
        raw_address = ", ".join(store_info)
        logger.info(f"[{idx}] [RAWADDRESS: {raw_address}]")
        formatted_addr = parse_address_intl(raw_address)

        # Street Address
        sta1 = formatted_addr.street_address_1
        sta2 = formatted_addr.street_address_2
        sta = ""
        if sta1 is not None and sta2 is not None:
            sta = sta1 + ", " + sta2
        elif sta1 is not None and sta2 is None:
            sta = sta1
        elif sta1 is None and sta2 is not None:
            sta = sta2
        else:
            sta = ""

        sta = sta.replace("Ste", "Suite")
        city = formatted_addr.city
        state = formatted_addr.state
        zip_code = formatted_addr.postcode
        country_code = "JP"
        phone = "".join(store_sel.xpath("//table//tr[last()-1]/td//text()"))

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath("//table//tr[last()-2]/td//text()")
                ],
            )
        )
        hours_of_operation = ""
        if hours:
            hours_of_operation = "; ".join(hours[:-1])

        store_number = page_url.split("TS&C=")[-1].split("&B=M")[0]
        item = SgRecord(
            locator_domain="pizza-la.co.jp",
            page_url=page_url,
            location_name=location_name,
            street_address=sta,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        sgw.write_row(item)
        logger.info(f"[{idx}] {item.as_dict()}")


def fetch_data(sgw: SgWriter):
    # Step1
    areas = [
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=1",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=2",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=3",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=4",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=5",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=6",
        "https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=7",
    ]
    logger.info(f"Areas: {areas}")

    # There are 7 areas as follows, and each area refers to each crawler,
    # based-on area name.
    # 7 Areas, out of these, this crawler refers to Hokkaido and Tohoku

    # Hokkaido and Tohoku＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=1
    # Kanto＞ https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=2
    # Koshinetsu / Hokuriku＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=3
    # Tokai＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=4
    # Kinki＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=5
    # Chugoku / Shikoku＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=6
    # Kyushu-Okinawa＞https://www.pizza-la.co.jp/TenpoTop.aspx?M=P&C=7

    urls1 = get_level1_store_locator_urls()

    # Step 2
    ret_urls2 = get_level2_store_locator_urls(urls1[1:2])

    # Step 3
    ret_urls3 = get_level3_store_locator_urls(ret_urls2)

    # Step 4
    japanese_k_normalized = normalize_the_store_locator_url(ret_urls3)

    # Step 5
    ret_urls4 = get_level4_store_locator_urls(japanese_k_normalized)

    # Step 6
    ret_urls5 = get_level5_store_locator_urls(ret_urls4)

    # Step 7
    ret_urls5_normalized = normalize_level5_the_store_locator_url(ret_urls5)

    # Step 8
    store_urls = get_level6_store_urls(ret_urls5_normalized)
    logger.info(f"Total Stores Count: {len(store_urls)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, num, store_url, sgw)
            for num, store_url in enumerate(store_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
