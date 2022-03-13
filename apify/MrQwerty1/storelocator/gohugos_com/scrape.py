from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    try:
        phone = tree.xpath(
            "//p[contains(text(), '-') and not(./*)]/text()|//p[./strong[contains(text(), 'Phone')]]/text()"
        )[0].strip()
    except:
        phone = SgRecord.MISSING
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    hours = tree.xpath(
        "//p[following-sibling::p[1][text()='Hours:']]/following-sibling::p/text()|//p[following-sibling::p[1][./*[text()='Hours:']]]/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = (
        " ".join(hours)
        .replace("Hours:", "")
        .replace("pm", "pm;")
        .replace("12pm;", "12pm")
        .strip()
    )
    if "(" in hoo:
        hoo = hoo.split("(")[0].strip()

    if hoo.endswith(";"):
        hoo = hoo[:-1]

    return phone, latitude, longitude, hoo


def fetch_data(sgw: SgWriter):
    api = "https://www.gohugos.com/store-locations/"
    r = session.get(api)
    tree = html.fromstring(r.text)
    sections = tree.xpath("//div[contains(@id, 'av_section_')]")

    for section in sections:
        location_type = (
            "".join(
                section.xpath(".//h2[contains(@class, 'av-special-heading')]/text()")
            )
            .replace(" Locations", "")
            .replace("  ", " & ")
        )
        articles = section.xpath(".//article")

        for a in articles:
            location_name = "".join(
                a.xpath(".//h3[@itemprop='headline']/text()")
            ).strip()
            page_url = "".join(a.xpath(".//a[text()='View Details']/@href")) or api

            line = a.xpath(
                ".//div[contains(@class,'iconbox_content_container')]/p[1]/text()"
            )
            line = list(filter(None, [l.strip() for l in line]))

            street_address = line[0]
            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[-1]
            if page_url == api:
                phone = SgRecord.MISSING
                latitude = SgRecord.MISSING
                longitude = SgRecord.MISSING
                hours_of_operation = SgRecord.MISSING
            else:
                phone, latitude, longitude, hours_of_operation = get_additional(
                    page_url
                )

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
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gohugos.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            )
        )
    ) as writer:
        fetch_data(writer)
