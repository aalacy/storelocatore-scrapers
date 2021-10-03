import datetime
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_map_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_hoo(slug):
    _tmp = []
    start_date = datetime.date.today().strftime("%Y-%m-%d")
    end_date = (datetime.date.today() + datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    url = f"{slug}?startDate={start_date}&endDate={end_date}"

    r = session.get(url, headers=headers)
    js = r.json()["availableDays"]
    for j in js:
        try:
            date = j.get("date")
            if not date:
                raise IndexError

            date = date.split("T")[0]
            day = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            j = j["hours"][0]
            start = j.get("open")
            end = j.get("close")
            _tmp.append(f"{day}: {start}-{end}")
        except IndexError:
            continue

    return ";".join(_tmp).replace(":00:00", ":00").replace(":30:00", ":30")


def get_urls():
    r = session.get("https://www.greatwolf.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//li[contains(@class, 'open')]/a/@href")


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.greatwolf.com{url}"

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), '{}')]/text()".format('"address":'))
    )
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"
    phone = j.get("telephone") or "<MISSING>"
    _map = j.get("hasMap") or ""
    latitude, longitude = get_map_from_google_url(_map)

    slug = "".join(tree.xpath("//div[@data-api-url]/@data-api-url"))
    hours_of_operation = get_hoo(slug)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.greatwolf.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
