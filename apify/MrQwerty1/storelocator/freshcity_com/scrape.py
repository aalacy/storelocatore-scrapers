from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-pf-type='Column' and .//iframe]")

    for d in divs:
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line.pop(0)
        phone = line.pop().replace("Phone:", "").strip()
        csz = line.pop()
        street_address = ", ".join(line)
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]

        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://freshcitykitchen.com/"
    page_url = "https://freshcitykitchen.com/pages/retail"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
