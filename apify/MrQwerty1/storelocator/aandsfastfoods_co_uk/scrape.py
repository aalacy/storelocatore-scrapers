from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, c, p):
    adr = parse_address(International_Parser(), line, city=c, postcode=p)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    urls = []
    data = {"action": "get_all_stores", "lat": "", "lng": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://aandsfastfoods.co.uk",
        "Connection": "keep-alive",
        "Referer": "https://aandsfastfoods.co.uk/our-locations/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    r = session.post(
        "https://aandsfastfoods.co.uk/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )
    js = r.json().values()
    for j in js:
        urls.append(j.get("gu"))

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1//text()")).strip()
    raw_address = ", ".join(
        tree.xpath("//div[contains(@class, 'store_locator_single_address')]/text()")
    )
    c = location_name.replace("Sam’s Chicken ", "")
    p = raw_address.split(", ")[-1].strip()
    street_address, city, state, postal = get_international(raw_address, c, p)
    if " " in postal:
        pp = postal.split()
        if pp[0] == pp[1]:
            postal = pp[0]

    if postal in street_address.upper():
        street_address = raw_address.split(", ")[0].strip()
        if len(street_address) < 7:
            street_address = " ".join(raw_address.split(", ")[:2])

    phone = "".join(
        tree.xpath(
            "//div[contains(@class, 'store_locator_single_contact')]/a[contains(@href, 'tel:')]/text()"
        )
    ).strip()
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lng]/@data-lng"))
    hours_of_operation = ";".join(
        tree.xpath("//h2[contains(text(), 'Hours')]/following-sibling::text()")
    ).replace(" o'Clock", "")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://aandsfastfoods.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
