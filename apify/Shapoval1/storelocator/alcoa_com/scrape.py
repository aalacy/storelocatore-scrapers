from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.alcoa.com/"
    page_url = "https://www.alcoa.com/global/en/who-we-are/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//p[./strong]")
    for d in div:

        location_name = "".join(d.xpath("./strong[1]/text()"))
        if location_name == "Pittsburgh" or location_name == "Alcoa Corporation":
            continue
        country_code = "".join(d.xpath(".//preceding::button[1]/text()"))
        phone = (
            "".join(d.xpath("./text()[last() - 2]"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        if phone.find("G4Z1K6") != -1 or phone.find("The Netherlands") != -1:
            phone = "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        ad = (
            "".join(d.xpath(".//strong[1]/following-sibling::text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        ad = " ".join(ad.split()).replace("Facility Production:", "").strip()
        if phone != "<MISSING>":
            ad = ad.split(f"{phone}")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        postal = postal.replace("CEP", "").strip()
        city = a.city or "<MISSING>"
        location_type = "".join(d.xpath(".//preceding::h6[1]/text()"))

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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
