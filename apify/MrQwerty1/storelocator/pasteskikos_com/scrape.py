import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    req = session.get(page_url, headers=headers)
    root = html.fromstring(req.text)
    states = root.xpath("//select[@id='estado']/option[@value!='']")
    for s in states:
        state = "".join(s.xpath("./text()"))
        _id = "".join(s.xpath("./@value"))
        data = {
            "indice": "2",
            "estado": _id,
        }
        req = session.post(api, headers=headers, data=data)
        tree = html.fromstring(req.text)
        cities = tree.xpath("//option")

        for c in cities:
            location_name = "".join(c.xpath("./text()"))
            _id = "".join(c.xpath("./@value"))
            data = {
                "indice": "1",
                "ciudad": _id,
            }
            r = session.post(api, headers=headers, data=data)
            j = r.json()

            raw_address = j.get("direccion") or ""
            try:
                postal = re.findall(r"\d{5}", raw_address).pop()
            except:
                postal = SgRecord.MISSING

            street_address, city = get_international(raw_address.replace(postal, ""))
            country_code = "MX"

            text = j.get("mapa") or ""
            latitude, longitude = get_coords_from_embed(text)

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
                raw_address=raw_address,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pasteskikos.com/"
    page_url = "https://www.pasteskikos.com/sucursales"
    api = "https://www.pasteskikos.com/acciones.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.pasteskikos.com",
        "Connection": "keep-alive",
        "Referer": "https://www.pasteskikos.com/sucursales",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
