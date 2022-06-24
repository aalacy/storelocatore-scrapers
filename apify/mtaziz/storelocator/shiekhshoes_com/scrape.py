from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import ssl
from tenacity import retry, stop_after_attempt
import tenacity


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


store_locator = "https://www.shiekh.com/storelocator/"
logger = SgLogSetup().get_logger("shiekhshoes_com")
logger.info(f"StoreLocator: {store_locator}")


headers = {
    "authority": "www.shiekh.com",
    "method": "GET",
    "path": "/storelocator/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "referer": "https://www.shiekh.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}


def get_api_urls():
    api_start_page_url = (
        "https://www.shiekh.com/storelocator/index/loadstore/?curPage=1"
    )
    r = get_response(api_start_page_url)
    logger.info(f"HTTPStatusCode: {r.status_code}")
    js = r.json()
    pagin = js["pagination"]
    pgsel = html.fromstring(pagin)
    data_last_page = int("".join(pgsel.xpath("//@data-last-page")))
    api_urls = []
    for pgnum in range(1, data_last_page + 1):
        apiurl = f"https://www.shiekh.com/storelocator/index/loadstore/?curPage={pgnum}"
        api_urls.append(apiurl)
    return api_urls


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(10))
def get_response(page_url):
    with SgRequests() as s2:
        r2 = s2.get(page_url, headers=headers)
        if r2.status_code == 200:
            return r2
        raise Exception(f"Please fix TimeoutExcetionError at {page_url} ")


def fetch_data():
    api_urls = get_api_urls()
    for pgn, url in enumerate(api_urls[0:]):
        r1 = get_response(url)
        storesjson = r1.json()["storesjson"]
        for idx, _ in enumerate(storesjson[0:]):
            store_name = _["store_name"]
            sn = _["storelocator_id"]
            ph = _["phone"]
            st = _["address"]
            lat = _["latitude"]
            lng = _["longitude"]
            page_url = _["rewrite_request_path"]
            page_url = f"https://www.shiekh.com/{page_url}"
            try:
                r2 = get_response(page_url)
                sel = html.fromstring(r2.text, "lxml")
                sta = sel.xpath('//*[contains(@itemprop, "streetAddress")]/text()')[0]
                city = sel.xpath('//*[contains(@itemprop, "addressLocality")]/text()')[
                    0
                ]
                state = sel.xpath('//*[contains(@itemprop, "addressRegion")]/text()')[0]
                c = sel.xpath('//*[contains(@itemprop, "addressCountry")]/text()')[0]
                trs = sel.xpath('//div[@id="open_hour"]//tr')
                hoo = []
                for tr in trs:
                    trstr = "".join(tr.xpath(".//text()"))
                    trstr = " ".join(trstr.split())
                    hoo.append(trstr)
                hoo = ", ".join(hoo)
                logger.info(f"HOO: {hoo}")
                item = SgRecord(
                    locator_domain="shiekh.com",
                    page_url=page_url,
                    location_name=store_name,
                    street_address=sta,
                    city=city,
                    state=state,
                    zip_postal="",
                    country_code=c,
                    store_number=sn,
                    phone=ph,
                    location_type="",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo,
                    raw_address=st,
                )
                logger.info(f"[{idx}] ITEM: {item.as_dict()}")
                yield item
            except:
                item = SgRecord(
                    locator_domain="shiekh.com",
                    page_url=page_url,
                    location_name=store_name,
                    street_address=st,
                    city="",
                    state="",
                    zip_postal="",
                    country_code="United States",
                    store_number=sn,
                    phone=ph,
                    location_type="",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation="",
                    raw_address=st,
                )
                logger.info(f"[{idx}] ITEM: {item.as_dict()}")
                yield item


def scrape():
    logger.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
