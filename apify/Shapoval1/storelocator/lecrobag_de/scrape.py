from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://lecrobag.de/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.lecrobag.de",
        "Connection": "keep-alive",
        "Referer": "https://www.lecrobag.de/shops-de/standorte.html",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "searchname": "",
        "searchzip": "Deutschland",
        "task": "search",
        "filter_catid": "",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "106",
        "zoom": "6",
        "format": "json",
        "geo": "",
        "latitude": "",
        "longitude": "",
        "limitstart": "0",
    }

    r = session.post(
        "https://www.lecrobag.de/shops-de/standorte.html", headers=headers, data=data
    )
    js = r.json()["features"]
    for j in js:

        info = j.get("properties").get("description")
        a = html.fromstring(info)
        address_line_lst = a.xpath('//span[@class="locationaddress"]/text()')
        address_line_lst = list(filter(None, [a.strip() for a in address_line_lst]))
        address_line = " ".join(address_line_lst)
        ad = "".join(address_line_lst[-2]).replace(",", "").strip()
        slug = j.get("properties").get("url")
        page_url = f"https://www.lecrobag.de{slug}"
        location_name = j.get("properties").get("name")
        b = parse_address(International_Parser(), address_line)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = "".join(address_line_lst[-3]).strip()
        postal = ad.split()[0].strip()
        country_code = "DE"
        if address_line.find("Polen") != -1:
            country_code = "PL"
        if address_line.find("Österreich") != -1:
            country_code = "AT"
        city = " ".join(ad.split()[1:]).strip()
        if city.find("/") != -1:
            city = city.split("/")[0].strip()
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("geometry").get("coordinates")[0]
        longitude = j.get("geometry").get("coordinates")[1]
        phone = "".join(a.xpath('//a[contains(@href, "tel")]//text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//i[@class="mml-calendar"]/following-sibling::text()'))
            .replace("\n", "")
            .replace("Öffnungszeiten:", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=address_line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
