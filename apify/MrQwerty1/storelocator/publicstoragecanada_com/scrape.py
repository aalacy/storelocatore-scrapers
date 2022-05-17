import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://publicstoragecanada.com/locations-sitemap.xml", headers=headers
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//url/loc[not(contains(text(), '/fr/'))]/text()")


def get_value(text):
    try:
        return text.split('"')[1]
    except IndexError:
        return SgRecord.MISSING


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'SelfStorage')]/text()")
    ).strip()
    if not text:
        text = "".join(
            tree.xpath("//script[contains(text(), 'LocalBusiness')]/text()")
        ).strip()
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    phone = j.get("telephone")

    store_number = get_value(
        "".join(tree.xpath("//script[contains(text(), 'locationid')]/text()"))
    )
    latitude = get_value(
        "".join(tree.xpath("//script[contains(text(), 'var lat')]/text()"))
    )
    longitude = get_value(
        "".join(tree.xpath("//script[contains(text(), 'var lng')]/text()"))
    )

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        d = h.get("dayOfWeek") or []
        day = ",".join(d)
        start = h.get("opens")
        end = h.get("closes")
        _tmp.append(f"{day}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
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
    locator_domain = "https://publicstoragecanada.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
