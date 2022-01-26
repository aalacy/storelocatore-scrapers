import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_urls():
    r = session.get("https://stores.next.co.uk/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@id='country-store']/option[@value!='']/@value")


def get_raw(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    lines = tree.xpath("//td[@class='first']/text()")
    lines = list(filter(None, [line.strip() for line in lines]))

    return " ".join(lines)


def get_street(page_url):
    line = get_raw(page_url)
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()

    return street_address


def get_city_postal(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city or ""
    postal = adr.postcode or ""
    return city, postal


def get_data(country, sgw: SgWriter):
    api = f"https://stores.next.co.uk/stores/country/{country}"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.lctr.results.push(')]/text()")
    ).split("\n")

    for t in text:
        if not t.strip().startswith("window.lctr.results.push("):
            continue

        t = t.split("window.lctr.results.push(")[1].split(");")[0]
        j = json.loads(t)
        _types = j.get("store_types") or []
        if 10 not in _types:
            continue

        _tt = []
        for _t in _types:
            if types_converter.get(str(_t)):
                _tt.append(types_converter.get(str(_t)))

        location_type = ";".join(_tt)
        store_number = j.get("location_id")
        page_url = f"https://stores.next.co.uk/results/infowindow/{store_number}"
        street_address = f"{j.get('AddressLine')} {j.get('street') or ''}".strip()
        street_address = " ".join(street_address.split())
        if len(street_address) < 10:
            street_address = get_street(page_url)
        city = j.get("city") or ""
        state = j.get("county")
        postal = j.get("PostalCode")
        if not postal:
            city, postal = get_city_postal(city)
        location_name = j.get("branch_name")
        phone = j.get("telephone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")

        _tmp = []
        days = ["mon", "tues", "weds", "thurs", "fri", "sat", "sun"]
        for d in days:
            start = j.get(f"{d}_open") or ""
            close = j.get(f"{d}_close") or ""
            if start.strip() != "0" and start.strip() and start.strip() != "Store":
                if len(start) == 3:
                    start = f"0{start}"

                _tmp.append(
                    f"{d.capitalize()}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                )

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            phone=phone,
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
    locator_domain = "https://www.next.co.uk/"
    types_converter = {
        "1": "Home Stores Only",
        "3": "Clearance Stores Only",
        "4": "Lingerie Room Stores Only",
        "5": "Return Locations Only",
        "6": "Schoolwear Stores Only",
        "8": "Express to Store Delivery",
        "9": "Ex Display Furniture",
        "10": "Lipsy Stores Only",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
