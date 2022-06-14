import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.douglas.it/it/l", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='link link--no-decoration list-view-item__link']/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.douglas.it{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = " ".join(" ".join(tree.xpath("//h1//text()")).split())
    street_address = " ".join(
        "".join(tree.xpath("//div[@class='store-address__line1']//text()")).split()
    )
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()
    line = tree.xpath("//div[@class='store-address__line2']//text()")
    line = list(filter(None, [li.strip() for li in line]))
    postal = line.pop(0)
    city = line.pop(0)
    country_code = "IT"
    phone = "".join(
        tree.xpath("//div[@class='store-detail-view__phone']//text()")
    ).strip()
    store_number = page_url.split("/")[-1]

    _tmp, _days = [], []
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    text = "".join(
        tree.xpath("""//script[contains(text(), '"LocalBusiness"')]/text()""")
    )
    js = json.loads(text, strict=False)
    for j in js:
        if j.get("@type") == "LocalBusiness":
            hours = j.get("openingHoursSpecification") or []
            for h in hours:
                day = str(h.get("dayOfWeek")).split("/")[-1]
                start = h.get("opens")
                end = h.get("closes")
                if start:
                    _tmp.append(f"{day}: {start}-{end}")
                    _days.append(day)
            break

    for day in days:
        if day not in _days:
            _tmp.append(f"{day}: Closed")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.douglas.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
