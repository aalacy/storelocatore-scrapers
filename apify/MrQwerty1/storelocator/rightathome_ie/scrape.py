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
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='row']/div[h2 and .//iframe]")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)
        line = d.xpath(".//p[contains(text(), 'Ph:')]//text()")
        if line[0][-1].isdigit():
            phone = line[0].replace("Ph:", "").strip()
        else:
            phone = line[1].strip()
        country_code = "IE"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rightathome.ie/"
    page_url = "https://www.rightathome.ie/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
