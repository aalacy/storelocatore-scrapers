from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    data = {
        "searchzip": "colombia",
        "task": "search",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "111",
        "zoom": "9",
        "format": "json",
        "geo": "",
        "limitstart": "0",
        "latitude": "",
        "longitude": "",
    }
    r = session.post(api, headers=headers, data=data)
    js = r.json()["features"]

    for j in js:
        p = j.get("properties") or {}
        source = p.get("description") or "<html>"
        slug = p.get("url")
        if slug:
            page_url = f"https://www.macpollo.com{slug}"
        else:
            page_url = api
        tree = html.fromstring(source)
        line = tree.xpath(".//span[@class='locationaddress']/text()")

        index = 0
        for li in line:
            index += 1
            if "\xa0" in li:
                break

        raw_address = " ".join(" ".join(line[:index]).replace("\xa0", " ").split())
        if raw_address.endswith(","):
            raw_address = raw_address[:-1]

        street_address, city, state, postal = get_international(raw_address)
        country_code = "CO"
        store_number = j.get("id")
        location_name = p.get("name")

        phone = "".join(tree.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()

        g = j.get("geometry") or {}
        latitude, longitude = g.get("coordinates") or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )
        text = " ".join(tree.xpath(".//span[@class='locationaddress']//text()"))
        try:
            hours_of_operation = text.split("Domicilios")[1].strip()
            if hours_of_operation.startswith("-"):
                hours_of_operation = hours_of_operation[1:].strip()
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
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.macpollo.com/"
    api = "https://www.macpollo.com/puntos-de-venta"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.macpollo.com",
        "Connection": "keep-alive",
        "Referer": "https://www.macpollo.com/puntos-de-venta",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests(proxy_country="co")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
