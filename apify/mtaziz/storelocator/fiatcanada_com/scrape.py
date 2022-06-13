from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests import SgRequests
from sglogging import SgLogSetup
from lxml import html
from concurrent import futures


locator_domain = "fiatcanada.com"
logger = SgLogSetup().get_logger(logger_name=locator_domain)
MISSING = SgRecord.MISSING


def get_hours(code):
    _tmp = []
    url = f"https://www.fiatcanada.com/en/dealers/{code}"
    r = session.get(url, headers=headers)
    logger.info(f"{url} Response: {r}")
    if r.status_code == 404:
        return
    try:
        tree = html.fromstring(r.text)
    except:
        return
    divs = tree.xpath("//div[@id='sales-tab']//p[@class='C_DD-week-day']")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[last()]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    codes = []
    hours = dict()
    api = "https://www.fiatcanada.com/data/dealers/expandable-radius?brand=fiat&longitude=-71.55160000000001&latitude=47.11749309813037&radius=20000"
    logger.info(f"API: {api}")
    r = session.get(api, headers=headers)
    logger.info(f"API Response: {r}")
    js = r.json()["dealers"]
    for j in js:
        codes.append(j.get("code"))

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_hours, code): code for code in codes}
        for future in futures.as_completed(future_to_url):
            time = future.result()
            code = future_to_url[future]
            hours[code] = time

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("province")
        postal = j.get("zipPostal")
        country_code = "CA"
        store_number = j.get("code")
        page_url = f"https://www.fiatcanada.com/en/dealers/{store_number}"
        location_name = j.get("name")
        phone = j.get("contactNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = hours.get(store_number)
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    logger.info("Scrape Started")
    CrawlStateSingleton.get_instance().save(override=True)
    session = SgRequests()
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": "https://www.fiatcanada.com/en/dealers",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    }

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STORE_NUMBER,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Scrape Finished")
