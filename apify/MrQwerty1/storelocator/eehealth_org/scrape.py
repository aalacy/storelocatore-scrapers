from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    api = "https://www.eehealth.org/mapi/public/LocationSearch.json?label=d6731d49-dfcb-4082-bb26-7e7b62940469&start=0&count=5000"
    r = session.get(api, headers=headers)
    js = r.json()["response"]["locations"]
    for j in js:
        urls.add(f'https://www.eehealth.org{j.get("locationUrl")}')

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='location-detail__title']/h1/text()")
    ).strip()
    adr1 = "".join(
        tree.xpath("//span[@class='location-detail__address-one']/text()")
    ).strip()
    adr2 = "".join(
        tree.xpath("//span[@class='location-detail__address-two']/text()")
    ).strip()
    street_address = f"{adr1} {adr2}".strip()
    city = "".join(
        tree.xpath("//span[@class='location-detail__address-city']/text()")
    ).strip()

    if street_address.find(city) != -1:
        street_address = street_address.split(city)[0].strip()
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()
    state = "".join(
        tree.xpath("//span[@class='location-detail__address-state']/text()")
    ).strip()
    postal = "".join(
        tree.xpath("//span[@class='location-detail__address-zip']/text()")
    ).strip()
    phone = (
        "".join(tree.xpath("//span[@class='location-detail__main-phone']/text()"))
        .replace("(CARE)", "")
        .strip()
    )
    if phone.find(":") != -1:
        phone = phone.split(":")[1].strip()
    if not phone:
        phone = "".join(
            tree.xpath("//p[./strong[contains(text(), 'Main Phone')]]/text()")
        ).strip()

    _tmp = []
    pp = tree.xpath("//span[@class='location-detail__office-hours']/p[1]/text()")
    pp = list(filter(None, [p.strip() for p in pp]))

    for p in pp:
        if len(p) > 1:
            _tmp.append(p)

    hours_of_operation = ";".join(_tmp)

    if not hours_of_operation:
        hours_of_operation = (
            "".join(tree.xpath("//span[@class='location-detail__office-hours']/text()"))
            .strip()
            .replace("\n", ";")
        )

    if hours_of_operation.lower().find("call") != -1:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
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
    locator_domain = "https://www.eehealth.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
