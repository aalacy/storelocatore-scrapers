from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
import os

logger = SgLogSetup().get_logger("taxassist")


_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://us.fatface.com/stores",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Cookie": "__cfduid=daf10bd77120abd062ff79ae36a3394561614035333; dwac_0da89386c839c79e6773009f39=jTksSzgK29bHn4ewF1OU7gstpVxp30TmWAk%3D|dw-only|||GBP|false|Europe%2FLondon|true; cqcid=acZGV7iE3z709qnlaDSpcnNUR5; cquid=||; sid=jTksSzgK29bHn4ewF1OU7gstpVxp30TmWAk; dwanonymous_c587c8d662b3833601b344f41b2494fb=acZGV7iE3z709qnlaDSpcnNUR5; dwsid=VX1DfcviX-HEIPyDsVVa7tNpymqaN8DRW7bkrUqO8Kw7SA-9PO10QK473Yp8gKK3BTyGRlqm73qA-yj0s13z7w==; s_fid=515E81C6AC83CB7E-139201ED3D830070; s_getNewRepeat=1614035353525-New; s_cc=true; scarab.visitor=%22457AE3AEEC97CE16%22; s_vi=[CS]v1|301A1CC577F7199A-400005B84D13BDA5[CE]; __cq_uuid=ab0JNNtOLkGoBEqJunjlYWMnfK; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _hjTLDTest=1; _hjid=dc9183c0-0b35-4025-b2bb-7b109fa47b38; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=0; _fbp=fb.1.1614035344290.1677450804; _uetsid=f0cad3b0756211eb821f59b490c0f61c; _uetvid=f0caf790756211ebb247ab8ba216d046; s_sq=fatfaceusproduction%3D%2526c.%2526a.%2526activitymap.%2526page%253D%25252Fstores%2526link%253DGBP%252520%2525C2%2525A3%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253D%25252Fstores%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.fatface.com%25252Fstores%2526ot%253DA; __cq_dnt=0; dw_dnt=0; selectedLocale=en_GB",
}
locator_domain = "https://www.taxassist.co.uk/"

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
        }
        return proxies
    else:
        return None


session = SgRequests().requests_retry_session()
session.proxies = set_proxies()
max_workers = 1


def fetchConcurrentSingle(page_url):
    response = request_with_retries(page_url)
    return page_url, bs(response.text, "lxml")


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original).replace("\t", "").replace("\n", "")


def parse_detail(soup2, link):
    location = json.loads(
        _fix(soup2.find("script", type="application/ld+json").string.strip())
    )
    if location["address"]["streetAddress"] == "Coming Soon":
        return None
    hours = []
    for _ in location["openingHoursSpecification"]:
        hour = f"{_['opens']}-{_['closes']}"
        if hour == "00:00-00:00":
            hour = "closed"
        hours.append(f"{_['dayOfWeek']}: {hour}")
    hours_of_operation = "; ".join(hours)
    if re.search(r"please contact", hours_of_operation, re.IGNORECASE):
        hours_of_operation = ""
    addr = parse_address_intl(soup2.select_one("address").text.strip())
    return SgRecord(
        page_url=link,
        location_type=location["@type"],
        location_name=location["name"],
        street_address=addr.street_address_1,
        city=location["address"]["addressLocality"] or addr.city,
        zip_postal=location["address"]["postalCode"],
        country_code="uk",
        latitude=location["geo"]["latitude"],
        longitude=location["geo"]["longitude"],
        phone=location["telephone"],
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    base_url = "https://www.taxassist.co.uk/locations"
    soup = bs(session.get(base_url).text, "lxml")
    links = [link["href"] for link in soup.select("main div.row a.primary.outline")]
    for page_url, sp1 in fetchConcurrentList(links):
        details = [dd["href"] for dd in sp1.select("main div.mt-auto a.outline")]
        if details:
            for page_url, sp2 in fetchConcurrentList(details):
                yield parse_detail(sp2, page_url)
        else:
            yield parse_detail(sp1, page_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
