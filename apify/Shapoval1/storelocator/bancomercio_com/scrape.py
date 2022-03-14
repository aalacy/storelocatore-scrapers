from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancomercio.com/"
    api_url = (
        "https://www.bancomercio.com/elbanco/categoria/canales-de-atencion/631/c-631"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./h2[contains(text(), "Agencias")]]/following-sibling::div[1]//table//tr[./td[p]]'
    )
    for d in div:

        page_url = "https://www.bancomercio.com/elbanco/categoria/canales-de-atencion/631/c-631"
        location_name = (
            "".join(d.xpath("./td[1]//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        if location_name == "<MISSING>":
            continue
        ad = (
            "".join(d.xpath("./td[2]//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "PE"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath("./td[4]//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath("./td[3]//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("mediodia", "").strip()
        )

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
