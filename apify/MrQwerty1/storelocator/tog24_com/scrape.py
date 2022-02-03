from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    part = line.split(",")[-1]
    ispostal = False
    if "," in line:
        for p in part:
            if p.isdigit():
                ispostal = True
                break

    if ispostal:
        adr = parse_address(International_Parser(), line, postcode=part)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    postal = adr.postcode or ""
    if city.upper() in postal:
        postal = postal.replace(city.upper(), "").strip()

    return street_address, city, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.tog24.com/apps/store-locator"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    coords = dict()
    text = "".join(
        tree.xpath("//script[contains(text(), 'markersCoords.push')]/text()")
    )
    for t in text.split("markersCoords.push"):
        if "lat:" not in t:
            continue
        lat = t.split("lat:")[1].split(",")[0].strip()
        lng = t.split("lng:")[1].split(",")[0].strip()
        _id = t.split("id:")[1].split(",")[0].strip()
        coords[_id] = (lat, lng)

    divs = tree.xpath("//div[@id='addresses_list']/ul/li")
    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='name']/text()")).strip()
        raw_address = "".join(d.xpath(".//span[@class='address']/text()")).strip()
        street_address, city, postal = get_international(raw_address)
        phone = "".join(d.xpath(".//span[@class='phone']/text()")).strip()
        store_number = "".join(d.xpath("./@onblur")).split("(")[1].replace(")", "")
        latitude, longitude = coords.get(store_number) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        _tmp = []
        hours = d.xpath(".//span[@class='hours']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        for h in hours:
            if "open" in h.lower() or "store" in h.lower():
                continue
            _tmp.append(h)
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.tog24.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
