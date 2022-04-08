from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=12L6BcVOeSdbPWxJt_7dUTweRrb4&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//placemark")
    for marker in markers:
        key = "".join(marker.xpath("./description/text()")).lower().strip()
        if ", " in key:
            key = key.split(", ")[0].strip()

        line = "".join(marker.xpath(".//coordinates/text()")).strip()
        lat, lng = line.split(",")[:2]
        coords[key] = (lng, lat)

    return coords


def fetch_data(sgw: SgWriter):
    coords = get_coords()
    page_url = "https://www.regencyfurniture.com/pages/store-locator"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='row']/div[@class='col-md-6']/p[./strong]")
    hours = tree.xpath("//hr/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours = ";".join(hours)

    for d in divs:
        hours_of_operation = hours
        location_name = "".join(d.xpath("./strong/text()")).strip()
        if "coming soon" in location_name.lower():
            hours_of_operation = "Coming Soon"
        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line.pop(0)
        if line[-1][0].isdigit() or line[-1][0] == "(":
            phone = line.pop()
        else:
            phone = SgRecord.MISSING

        line = line[0]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        lat, lng = coords.get(city.lower()) or (SgRecord.MISSING, SgRecord.MISSING)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=lat,
            longitude=lng,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.regencyfurniture.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
