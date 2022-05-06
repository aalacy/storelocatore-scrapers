from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    try:
        phone = (
            tree.xpath("//p[contains(text(), 'Tel.:')]/text()")[0]
            .replace("Tel.:", "")
            .strip()
        )
    except IndexError:
        phone = SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//div[@class='warenhausZeiten']//strong")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        _tmp.append(f"{day}: {inter}")

    return phone, ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.famila-nordost.de/wp-admin/admin-ajax.php"
    data = '-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="action"\r\n\r\nmmp_map_markers\r\n-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="type"\r\n\r\nmap\r\n-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="id"\r\n\r\n1\r\n-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="custom"\r\n\r\n\r\n-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="all"\r\n\r\nfalse\r\n-----------------------------18064270863960691744385378085\r\nContent-Disposition: form-data; name="lang"\r\n\r\nnull\r\n-----------------------------18064270863960691744385378085--\r\n'
    r = session.post(api, headers=headers, data=data)
    js = r.json()

    for j in js:
        adr = j.get("address") or ""
        raw_address = adr.replace("<br>", ", ")
        street_address = adr.split("<br>")[0].strip()
        cz = adr.split("<br>")[1].strip()
        postal = cz.split()[0].replace(",", "").strip()
        city = (
            cz.replace(postal, "").replace(",", "").replace("Deutschland", "").strip()
        )
        if "(" in city:
            city = city.split("(")[0].strip()
        country_code = "DE"
        store_number = j.get("id")
        location_name = j.get("name")
        page_url = j.get("link")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.famila-nordost.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "multipart/form-data; boundary=---------------------------18064270863960691744385378085",
        "Origin": "https://www.famila-nordost.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
