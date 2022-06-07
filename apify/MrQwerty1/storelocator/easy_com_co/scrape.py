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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    page_url = "https://www.easy.com.co/donde-estamos/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@id='stores']/div")
    t = "".join(tree.xpath("//script[contains(text(), 'var imagenes =')]/text()"))
    t = t.split("var imagenes =")[1].split("];")[0] + "]"
    texts = eval(t)

    for d in divs:
        country_code = "CO"
        location_name = "".join(d.xpath("./a/text()")).strip()
        line = d.xpath(".//li//text()")
        line = list(
            filter(
                None,
                [li.replace("\u200b", "").replace("\xa0", " ").strip() for li in line],
            )
        )

        line.pop(0)

        if line[1] == "Cómo llegar:":
            raw_address = line.pop(0)
        else:
            raw_address = " ".join(line[:2])

        raw_address = raw_address.replace(":", "").strip()
        line = line[2:]

        phone = SgRecord.MISSING
        if line[-1][-1].isdigit():
            phone = line.pop().replace(":", "").strip()
        else:
            if "Teléfono" in line:
                phone = line.pop(line.index("Teléfono") + 1).replace(":", "").strip()

        _tmp = []
        write = False
        for li in line:
            if "Horario" in li:
                write = True
                continue
            if li == ":":
                continue
            if "Celular" in li or "Teléfono" in li or "Consulta" in li or "<" in li:
                break
            if write:
                _tmp.append(li.replace(": ", ""))

        hours_of_operation = ";".join(_tmp)
        store_number = "".join(d.xpath("./a/@id")).replace("t", "")
        street_address, city, state, postal = get_international(raw_address)
        text = texts[int(store_number)]
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
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.easy.com.co/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
