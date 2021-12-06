from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, state=""):
    if state:
        adr = parse_address(International_Parser(), line, state=state)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    r = session.get("https://westvillenyc.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='btn-sketch text-white']/@href")


def get_data(page_url, sgw: SgWriter):
    locator_domain = page_url.replace("/shop-finder", "")
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var storesData =')]/text()"))
    text = text.split("var storesData =")[1].split("];")[0] + "]"
    js = eval(text)
    for j in js:
        location_name = j.get("displayName")
        store_number = j.get("key") or ""
        country_code = store_number.split("-")[1]
        phone = j.get("phone")
        state = j.get("regionKey") or ""
        source = j.get("address") or "<html></html>"
        root = html.fromstring(source)
        raw_address = " ".join(root.xpath("//text()")).strip()
        street_address, city, state, postal = get_international(raw_address, state)
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("openingDays") or {}
        for k, v in hours.items():
            _tmp.append(f"{k}: {v}".replace("&nbsp;", " "))
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
            raw_address=raw_address,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = [
        "https://www.amway.sg/shop-finder",
        "https://www.amway.my/shop-finder/",
        "https://www.amway.id/id/shop-finder",
        "https://www.amway.com.vn/vn/shop-finder",
        "https://www.amway.com.ph/ph/shop-finder",
        "https://www.amway.co.th/shop-finder",
    ]

    with futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
