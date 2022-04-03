import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from tenacity import retry, stop_after_attempt
from sglogging import sglog


DOMAIN = "thrivent.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_hoo(page_url):
    r = session.get(page_url)
    logger.info(f"HOO Page: {page_url}, Response: {r.status_code}")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.JSContext =')]/text()")
    )

    try:
        js = json.loads(text.split("window.JSContext =")[1].replace(";", ""))["profile"]
    except:
        return ""
    source = js.get("office_hours") or "<html></html>"
    root = html.fromstring(source)

    return ";".join(root.xpath("//text()"))


def get_states():
    r = session.get("https://local.thrivent.com/directory")
    logger.info(f"get_states Response: {r.status_code}")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='Directory-listLink']/@href")


@retry(stop=stop_after_attempt(3))
def generate_links():
    urls = []
    states = get_states()
    for state in states:
        s = f"https://local.thrivent.com/{state}.json"
        r = session.get(s)
        js = r.json()["directoryHierarchy"]
        urls += list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://local.thrivent.com/{state['url']}.json"
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter, retry=0):
    try:
        r = session.get(url)
        logger.info(f"get_data Page: {url}, Response: {r.status_code}")
        j = r.json()["profile"]
    except:
        if retry < 3:
            return get_data(url, sgw, retry + 1)
        else:
            return

    page_url = j.get("c_baseURL") or url.replace(".json", "")
    location_name = j.get("name")
    a = j.get("address")

    street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")
    country_code = a.get("countryCode")
    store_number = j.get("corporateCode")
    phone = j.get("mainPhone").get("display")
    latitude = j["yextDisplayCoordinate"]["lat"]
    longitude = j["yextDisplayCoordinate"]["long"]
    try:
        days = j["hours"]["normalHours"]
    except KeyError:
        days = []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start"))
            end = str(interval.get("end"))

            if len(start) == 3:
                start = f"0{start}"

            if len(end) == 3:
                end = f"0{end}"

            if start == "0":
                start = "1200"

            line = f"{day}:  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}:  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or get_hoo(page_url)
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

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
        latitude=latitude,
        longitude=longitude,
        locator_domain=DOMAIN,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = generate_links()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    logger.info(f"Started Crawling: {DOMAIN}")
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
