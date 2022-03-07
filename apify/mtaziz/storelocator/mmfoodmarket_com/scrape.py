from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import json
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from sgpostal.sgpostal import parse_address_intl


website = "mmfoodmarket_com"
logger = SgLogSetup().get_logger(logger_name=website)
headers = {
    "Cookie": "analytics_session=true; _gcl_au=1.1.327023937.1637854042; ABTasty=uid=yxtcpyram8vhsj47&fst=1637854042067&pst=1637860016399&cst=1643461523582&ns=3&pvt=26&pvis=7&th=795149.0.5.5.1.1.1643461574199.1643463931542.1; _ga_MHHPDZZE1M=GS1.1.1637881102.4.0.1637881102.0; _ga=GA1.2.375507378.1637854042; _mm_food_market_session=eGgyX7BCzi91xbFTVgyzuQdkJy7C0F5K7FSnc9jdobcpXAAwO7y7aH3cNOhvhUzLRvTZSdhxRDTQeuuLk%2FCcx7b0XyF%2FRX7xmiqkQOk6M8gq6mHRg4VpOVF2UCqoTgjKz3M8Mb8BS9Lox41vicvPeA99UkG3Jtf6TtR8dwWT7t%2Bc2aEpXMYjuqUhWoR%2BgpJF9WsMZb%2BD19zdhvluI8jNGbA25sI7UZHPCsyReGWTx7UR9lnXha5rjxPm68cdZK0XweSMywaSGPX5wGXULoHf1yJhO7Ybkyz7ag%3D%3D--YB8hsb%2Fp8Mo4%2BuIZ--mc57LK7r%2Br7tmEpeVu7Zqw%3D%3D; default_store_id=; price_region=; rsci_vid=e72c44b5-c622-5d52-c79d-23b341244701; _fbp=fb.1.1637854044673.1709124546; _hjSessionUser_2250455=eyJpZCI6IjU0NjAyYWIzLWEyYmEtNTg2NS05NjIyLTg2YTMxNGU1YmY4OCIsImNyZWF0ZWQiOjE2Mzc4NTQwNDQ0OTQsImV4aXN0aW5nIjp0cnVlfQ==; _uetvid=2fe24e104e0411ecb417b59e7542b23c; ABTastySession=mrasn=&sen=11&lp=https%253A%252F%252Fmmfoodmarket.com%252F; _mm_food_market_session=Gg%2F6G0OmfmLr0Gx1oJIl9FD5epP%2FyrazJcau3WlLpSQPjhf%2Frmg7OAqNy5FZo1I3KSS72gJh3XjV3VGN2pgAJDwFBECRPBLa%2BHsJgy6quMhtjwUOcOzcJEUZ8tMLYvdj6Tao0a6DwYBRt6sMEVQ8J7PQkPrQl9rTxqf1Czhu0eTGBJGrkxyWycB5it3WIPXV4StfmRozHES1MuwOo%2BFp4sEOa0U%2BKODVlu3wGw%2FYTr%2Bqup9Y4DAipoUj0ru7bDDz0J6vLo8kMtZo86KTW%2Fo3RUdmvpXr9SrYPA%3D%3D--9tyquG6KrQE7wFQC--%2FwKuq02pxCyVlYF6nbcGpQ%3D%3D; default_store_id=; price_region="
}
DOMAIN = "mmfoodmarket.com"
MISSING = SgRecord.MISSING
MAX_WORKERS = 10


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(10))
def get_response_new(url):
    with SgRequests(verify_ssl=False) as http:
        r1 = http.get(url, headers=headers)
        if r1.status_code == 200:
            logger.info(f"HTTP Status Code: {r1.status_code}")
            return r1
        elif r1.status_code == 404:
            logger.info(f"URL does not exist! {r1.status_code}")
            return
        else:
            raise Exception(f"Please fix the issue of redirection{url}")


def get_hoo(sel):
    hoo = []
    hours_obj = sel.xpath('//p[contains(@class, "store-hours__day")]')
    for ho in hours_obj:
        ho1 = ho.xpath(".//text()")
        ho1 = [" ".join(i.split()) for i in ho1]
        ho1 = [i for i in ho1 if i]
        ho1 = ": ".join(ho1)
        hoo.append(ho1)
    hoo = ", ".join(hoo)
    return hoo


def parse_sta(rawadd):
    pai = parse_address_intl(rawadd)
    sta1 = pai.street_address_1
    sta2 = pai.street_address_2
    street_address = ""
    if sta1 is not None and sta2 is None:
        street_address = sta1
    elif sta1 is None and sta2 is not None:
        street_address = sta2
    elif sta1 is not None and sta2 is not None:
        street_address = sta1 + ", " + sta2
    else:
        street_address = "<MISSING>"
    return street_address


def fetch_records(storenum, sgw: SgWriter):
    url = f"https://mmfoodmarket.com/en/store_locations/{storenum}"
    logger.info(f"[{storenum}] Pulling data from {url}")

    r = get_response_new(url)
    if r is None:
        logger.info(f"[{storenum}] URL does not exist: {url}")
        return
    else:
        sel = html.fromstring(r.text, "lxml")
        sel = html.fromstring(r.text, "lxml")
        rsta = sel.xpath(
            '//script[contains(@type, "application/ld+json") and contains(text(), "LocalBusiness")]/text()'
        )
        js = json.loads("".join(rsta))
        title = js["name"].strip()
        link = js["url"].strip()
        address = js["address"]
        phone = js["telephone"].strip()
        city = address["addressLocality"].strip()
        state = address["addressRegion"].strip()
        street = ""
        street1 = address["streetAddress"]
        street2 = (
            js["hasMap"].split("dir//")[1].split(city)[0].replace("+", " ").strip()
        )
        street2 = street2.replace("%2C", ",")

        if street1:
            street = street1
        else:
            street = street2
        street = street.replace("%23", "#")

        storeid = link.split("store_id=")[1].strip()
        link = "https://mmfoodmarket.com/en/store_locations/" + storeid
        pcode = js["hasMap"].split(state)[1].replace("+", " ").strip()

        pcode = pcode.replace("-2A%231Lacombe", "T4L1Y8")

        lat = ""
        lng = ""
        loc_type = ""
        hours_of_operation = get_hoo(sel)
        latlng = sel.xpath(
            '//div[contains(@class, "store-results__map store-results__map--location")]/@data-google-map'
        )
        ll_js = json.loads("".join(latlng))
        ll_js_points = ll_js["points"][0]
        lat = ll_js_points["coordinates"][1]
        lng = ll_js_points["coordinates"][0]
        isexpress = ll_js_points["isExpress"]
        if isexpress is False:
            loc_type = "Traditional"
        else:
            loc_type = "Express"
        raw_address = ll_js_points["simpleAddress"]
        if raw_address == "5124 AB-2A #1 Lacombe AB T4L 1Y8":
            pcode = "T4L 1Y8"
        parsed_street_address = parse_sta(raw_address)

        if street == "72, boulevard St. Jean Baptiste local 156":
            parsed_street_address = street

        item = SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=title,
            street_address=parsed_street_address,
            city=city,
            state=state,
            zip_postal=pcode,
            country_code="CAN",
            store_number=storeid,
            phone=phone,
            location_type=loc_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    # Traditional Stores: Last store id found to be 543
    # So the max. id considered to be 600
    # If possible id does not match, HTTP status happens to return 404
    # if possible store id does match that means HTTP status happens to be 200
    # Express Stores ID falls between 3800 and 3999
    # Express Stores ID may be fallen between 3000 and 3999 as well.
    # We don't need to scrape the data for Express stores

    START_STORENUM = 0
    END_STORENUM = 600
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        store_data = [
            executor.submit(fetch_records, storenum, sgw)
            for storenum in range(START_STORENUM, END_STORENUM)
        ]
        tasks.extend(store_data)
        for future in as_completed(tasks):
            record = future.result()
            if record is not None or record:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
