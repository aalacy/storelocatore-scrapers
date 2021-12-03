import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = str(h.get("dayOfWeek"))
        if day.find("/") != -1:
            day = day.split("/")[-1].strip()
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{day} {opens} - {closes}"
        if opens == closes:
            line = f"{day} Closed"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://stores.ashleyfurniture.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), 'https://stores.ashleyfurniture.com/store/')]/text()"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://ashleyfurniture.com/"
    page_url = str(url)
    if page_url.count("/") != 8:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Request-Id": "|ncIOD.+o+8f",
        "Connection": "keep-alive",
        "Referer": f"{page_url}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
    j = json.loads(div)
    a = j.get("address")
    street_address = (
        str(a.get("streetAddress"))
        .replace("&#39;", "`")
        .replace("&#194;", "Â")
        .replace("&#233;", "é")
        .strip()
        or "<MISSING>"
    )
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry") or "<MISSING>"
    location_name = j.get("name") or "<MISSING>"
    location_type = j.get("@type") or "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    hours = j.get("openingHoursSpecification") or "<MISSING>"
    hours_of_operation = "<MISSING>"
    if hours != "<MISSING>":
        hours_of_operation = get_hours(hours)
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"
    latitude = j.get("geo").get("latitude") or "<MISSING>"
    longitude = j.get("geo").get("longitude") or "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
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
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
