from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    out = dict()
    r = session.get(
        "https://www.google.com/maps/d/kml?forcekml=1&mid=1GOcPBmfa1u1f8ZORKRWPRbVd6nhmC-wJ"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//placemark")
    for m in markers:
        name = (
            "".join(m.xpath("./name/text()"))
            .lower()
            .replace("-", "")
            .replace("local cantina", "")
            .strip()
        )
        lat, lng = "".join(m.xpath(".//coordinates/text()")).split(",")[:2]
        lng, lat = lat.strip(), lng.strip()
        out[name] = (lat, lng)

    return out


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='wpb_column vc_column_container vc_col-sm-12 vc_col-lg-4 vc_col-md-4']"
    )
    coords = get_coords()

    for d in divs:
        location_name = "".join(d.xpath(".//h1/text()")).strip()
        raw_address = "".join(d.xpath(".//h1/following-sibling::p/text()"))
        if not raw_address:
            continue

        line = raw_address.split(", ")
        state, postal = line.pop().split()
        city = line.pop()
        street_address = ", ".join(line)

        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/@href"))
            .replace("%20", "")
            .replace("tel:", "")
        )
        key = location_name.lower()
        if key == "gahana":
            key = "gahanna"
        if key == "hillard":
            key = "hilliard"
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://localcantina.com/"
    page_url = "https://localcantina.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
