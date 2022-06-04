from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    out = dict()
    r = session.get(
        "https://www.google.com/maps/d/kml?forcekml=1&mid=1F0jJrd8rIIp_9-yBu-iK7rmo3m4JrTQW"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//placemark")
    for m in markers:
        key = "".join(m.xpath("./description/text()")).split(",")[0].strip().lower()
        lat, lng = "".join(m.xpath(".//coordinates/text()")).split(",")[:2]
        lng, lat = lat.strip(), lng.strip()
        out[key] = (lat, lng)

    return out


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-md-4 mb-5']")
    coords = get_coords()

    for d in divs:
        location_name = "Wienerwald"
        raw_address = " ".join(" ".join(d.xpath(".//h5/text()")).split())
        postal, city = d.xpath(".//h5/text()")[0].split()
        street_address = d.xpath(".//h5/text()")[-1].strip()
        key = street_address.lower()

        line = d.xpath(".//h6/text()")
        line = list(filter(None, [li.strip() for li in line]))
        phone = line.pop(0).replace("Tel.", "").strip()
        hours_of_operation = line.pop()
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="AT",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.wienerwald.at/"
    page_url = "https://www.wienerwald.at/standorte-restaurants.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
