from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_street_state(line):
    adr = parse_address(International_Parser(), line, country="AU")
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    state = adr.state or SgRecord.MISSING

    return street, state


def get_tree(page_url):
    r = session.get(page_url, headers=headers)
    return html.fromstring(r.text)


def get_urls():
    tree = get_tree("https://www.givenchy.com/int/en/storelocator")
    return tree.xpath("//select[@class='countries-list form-input']/option/@data-href")


def get_additional(page_url):
    tree = get_tree(page_url)
    text = " ".join(
        "".join(
            tree.xpath("//script[contains(text(), 'defaultLocation')]/text()")
        ).split()
    )
    try:
        lat = text.split("lat:")[1].split(",")[0].strip()
        lng = text.split("lng:")[1].split("}")[0].strip()
        if lat == "null" or lng == "null":
            raise IndexError
    except IndexError:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[@class='opening-infos']//li")
    for h in hours:
        day = "".join(h.xpath("./span[1]/text()")).strip()
        inter = "".join(h.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp), lat, lng


def get_data(slug, sgw: SgWriter):
    country_url = f"https://www.givenchy.com{slug}"
    country_code = slug.split("filter_country=")[1].split("&")[0].upper()
    tree = get_tree(country_url)

    divs = tree.xpath("//a[@class='store-block']")
    for d in divs:
        slug = "".join(d.xpath("./@href"))
        store_number = slug.split("=")[-1]
        page_url = f"https://www.givenchy.com/us/en-US/store?StoreID={store_number}"
        location_name = " ".join("".join(d.xpath(".//h2//text()")).split())
        address = d.xpath(".//div[@class='store-address']//text()")
        address = list(filter(None, [a.replace(",", "").strip() for a in address]))
        raw_address = ", ".join(address)
        if country_code == "US":
            city = address.pop()
            address.pop()
            sz = "".join(d.xpath(".//span[@class='store-postal-code']/text()")).strip()
            if " " in sz:
                state, postal = sz.split()
            else:
                state, postal = SgRecord.MISSING, sz
            street_address = ", ".join(address)
        elif country_code in {"AU", "JP", "KR", "QA", "SG"}:
            city = address.pop()
            postal = address.pop()
            street_address, state = get_street_state(", ".join(address))
        else:
            street_address, city, state, postal = get_international(raw_address)

        phone = "".join(d.xpath(".//div[@class='store-contact']/text()")).strip()
        hours_of_operation, latitude, longitude = get_additional(page_url)

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
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.givenchy.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.givenchy.com/int/en/homepage",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    session = SgRequests(proxy_country="au")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
