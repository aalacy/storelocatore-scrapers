from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import re
from lxml import html

logger = SgLogSetup().get_logger("golftec_com")
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}

locator_domain = "golftec.com"
china_url = "https://www.golftec.cn/golf-lessons/nanshan"
jp_url = "https://golftec.golfdigest.co.jp/"
hk_url = "https://www.golftec.com.hk/locations"
logger.info(f"HK Store Locator: {hk_url}")
page_url_hk = "https://www.golftec.com.hk/golf-lessons/hong-kong"

MAX_WORKERS = 1


def fetch_hk(page_url, http, sgw: SgWriter):
    session = SgRequests()
    text = session.get(page_url).text
    page = html.fromstring(text)
    data = json.loads(page.xpath('//script[@type="application/ld+json"]/text()')[0])

    location_name = data["name"]

    address = data["address"]
    street_address = address["streetAddress"]
    city = address["addressLocality"]
    postal = address["postalCode"]
    country_code = address["addressCountry"]

    address_details = page.xpath(
        '//div[contains(@class, "center-details__details")]/h5/text()'
    )
    raw_address = " ".join(", ".join(address_details).split()).rstrip(",")
    if not street_address:
        street_address = "4/F Admiralty Centre, Tower II, 18 Harcourt Road"
    if "Admiralty, Hong Kong" in city:
        city = "Admiralty"

    geo = data["geo"]
    latitude = geo["latitude"]
    longitude = geo["longitude"]
    phone = data["contactPoint"].get("telephone")
    hours = []
    for hour in data["openingHoursSpecification"]:
        day = re.sub("http://schema.org/", "", hour["dayOfWeek"])
        opens = hour["opens"]
        closes = hour["closes"]

        hours.append(f"{day}: {opens}-{closes}")
    hours_of_operation = ",".join(hours)

    item = SgRecord(
        locator_domain="golftec.com.hk",
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        phone=phone,
        raw_address=raw_address,
    )
    logger.info(f"Item: {item}")
    sgw.write_row(item)


def fetch_cn(url, http, sgw: SgWriter):
    logger.info(url)
    res = http.get(url, headers=headers)
    sp1 = bs(res.text, "lxml")
    ss = json.loads(sp1.find("script", type="application/ld+json").string)
    raw_address = (
        sp1.find("p", string=re.compile(r"地址")).text.replace("地址", "").replace("：", "")
    )
    city = "市" + raw_address.split("市")[0]
    street_address = raw_address.split("市")[-1]
    hours = [
        ": ".join(hh.stripped_strings)
        for hh in sp1.select("div.center-details__hours ul li")
    ]
    item = SgRecord(
        page_url=url,
        location_name=ss["name"],
        street_address=street_address,
        city=city,
        country_code="China",
        latitude=ss["geo"]["latitude"],
        longitude=ss["geo"]["longitude"],
        phone=ss["contactPoint"]["telephone"],
        hours_of_operation="; ".join(hours),
        locator_domain="golftec.cn",
        raw_address=raw_address,
    )
    logger.info(f"Item: {item}")
    sgw.write_row(item)


def fetch_jp(idx, page_url, http, sgw: SgWriter):
    logger.info(f"[{idx}] PullingContentFrom: {page_url}")
    sp2 = bs(http.get(page_url, headers=headers).text, "lxml")
    s_data = json.loads(sp2.find("script", type="application/ld+json").string)
    raw_address = (
        " ".join(sp2.select_one("p.studioAccess__detail__adress").stripped_strings)
        .replace("〒", "")
        .strip()
    )
    zip_postal = raw_address.split()[0]
    s_c = " ".join(raw_address.split()[1:])
    ss = state = city = street_address = ""
    if "都" in s_c:
        ss = s_c.split("都")[-1]
        state = s_c.split("都")[0] + "都"
    elif "県" in s_c:
        ss = s_c.split("県")[-1]
        state = s_c.split("県")[0] + "県"
    elif "府" in s_c:
        ss = s_c.split("府")[-1]
        state = s_c.split("府")[0] + "府"

    if "市" in ss:
        city = ss.split("市")[0] + "市"
        street_address = ss.split("市")[-1]
    else:
        street_address = ss

    hours = sp2.select_one(
        "dl.p-studioInfo__desc.-businessHours dd.p-studioInfo__desc__content"
    ).text.strip()
    coord = (
        sp2.select_one("p.studioAccess__detail__map")
        .iframe["src"]
        .split("!1d")[1]
        .split("!2m")[0]
        .split("!3m")[0]
        .split("!3d")
    )
    lng = coord[0].split("!2d")[-1]
    item = SgRecord(
        page_url=page_url,
        location_name=s_data["name"],
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code="JP",
        latitude=coord[1],
        longitude=lng,
        phone=s_data["telephone"],
        hours_of_operation=hours,
        locator_domain="golftec.golfdigest.co.jp",
        raw_address=raw_address,
    )
    logger.info(f"ITEM: {item.as_dict()}")
    sgw.write_row(item)


def get_store_urls():
    s = SgRequests(proxy_country="us")
    r = s.get("https://golftec.golfdigest.co.jp/studio/", headers=headers)
    sel = html.fromstring(r.text)
    store_urls = [
        "https://golftec.golfdigest.co.jp" + i
        for i in sel.xpath('//li[contains(@class, "p-studio__store-list")]/a/@href')
    ]
    return store_urls


def fetch_data(sgw: SgWriter):
    store_urls_jp = get_store_urls()
    logger.info(f"StoreCountInJapanChinaHongKong: {len(store_urls_jp)}")
    with SgRequests(proxy_country="us") as http:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = []

            # Hong Kong
            task_hk = [executor.submit(fetch_hk, page_url_hk, http, sgw)]
            tasks.extend(task_hk)

            # China
            task_cn = [executor.submit(fetch_cn, china_url, http, sgw)]
            tasks.extend(task_cn)

            # Japan
            task_jp = [
                executor.submit(fetch_jp, idx, store_url, http, sgw)
                for idx, store_url in enumerate(store_urls_jp[0:])
            ]
            tasks.extend(task_jp)

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
            ),
            duplicate_streak_failure_factor=1500,
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
