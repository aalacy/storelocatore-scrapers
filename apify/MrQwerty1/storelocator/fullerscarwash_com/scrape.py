from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    phone = "".join(
        tree.xpath("//div[@id='carwash']//div[@class='phone']/text()")
    ).strip()
    hours = tree.xpath("//div[@id='carwash']//div[@class='time']/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.LatLng')]/text()")
    )
    try:
        lat = text.split("new google.maps.LatLng('")[1].split("'")[0]
        lng = text.split("new google.maps.LatLng(")[1].split("','")[1].split("')")[0]
    except:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return phone, lat, lng, ";".join(hours)


def fetch_data(sgw: SgWriter):
    api = "https://www.fullerscarwash.com/location/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'location location-')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        slug = "".join(d.xpath(".//a[@class='btn btn-red']/@href"))
        page_url = f"https://www.fullerscarwash.com{slug}"
        line = d.xpath(".//div[@class='address']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        csz = line.pop()
        street_address = ", ".join(line)
        city = csz.split(",")[0].strip()
        state, postal = csz.split(",")[1].strip().split()
        phone, latitude, longitude, hours_of_operation = get_additional(page_url)

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.fullerscarwash.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
