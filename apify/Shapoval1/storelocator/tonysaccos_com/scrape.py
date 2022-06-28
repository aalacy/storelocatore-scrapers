from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tonysaccos.com"
    page_url = "https://tonysaccos.com/locations"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        "//div[./div[contains(@class, 'wpb_column vc_column_container vc_col-sm-6')]]"
    )
    for b in block:

        ad = b.xpath(".//h3/span//text()")
        ad = list(filter(None, [b.strip() for b in ad]))
        phone = "".join(ad[-1]).replace("Phone:", "").strip()
        adr = (
            " ".join(ad)
            .split("Tony Sacco’s")[1]
            .split("Phone")[0]
            .replace("Great Lakes Mall", "")
            .strip()
        )

        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        location_name = "".join(b.xpath(".//h2/span/text()"))
        text = "".join(b.xpath(".//iframe/@src"))
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = " ".join(b.xpath(".//span[contains(text(), 'pm')]/text()"))

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
