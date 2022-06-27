import json
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_id():
    r = session.get("https://www.westfield.co.nz/", headers=headers)
    return "".join(re.findall(r'"buildId":"(.+?)"', r.text))


def get_urls():
    urls = []
    domains = ["https://www.westfield.com.au/", "https://www.westfield.co.nz/"]

    for domain in domains:
        cc = domain.split(".")[-1].replace("/", "").upper()
        api = f"{domain}_next/data/{token}/en-{cc}.json"
        r = session.get(api, headers=headers)
        js = r.json()["pageProps"]["nationalHeaderData"]["centres"]

        for j in js:
            slug = j.get("slug")
            url = f"{domain}_next/data/{token}/en-{cc}/{slug}.json"
            urls.append(url)

    return urls


def get_hoo(api):
    _tmp = []
    r = session.get(api, headers=headers)

    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'centreTradingHours')]/text()")
    )
    text = text.split('"centreTradingHours":')[1].split("}]},")[0] + "}]"
    js = json.loads(text)
    if len(js) > 7:
        js = js[:7]

    for j in js:
        day = j.get("dayOfTheWeek")
        if j.get("isClosed"):
            _tmp.append(f"{day}: Closed")
            continue

        start = j.get("openingTime")
        end = j.get("closingTime")
        _tmp.append(f"{day}: {start}-{end}")

    return ";".join(_tmp)


def get_data(api, sgw: SgWriter):
    locator_domain = api.split("_next")[0]
    country_code = api.split("en-")[1].split("/")[0]
    slug = api.split("/")[-1].replace(".json", "")
    page_url = f"{locator_domain}{slug}"
    r = session.get(api, headers=headers)
    j = r.json()["pageProps"]["centre"]

    location_name = j.get("title")
    street_address = j.get("physicalAddress")
    city = j.get("suburb")
    state = j.get("state")
    postal = j.get("postcode")
    phone = j.get("telephoneNumber")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    hoo_url = f"{locator_domain}{slug}/opening-hours"
    try:
        hours_of_operation = get_hoo(hoo_url)
    except:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    token = get_id()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
