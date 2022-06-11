import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mirror.co"
    page_url = "https://www.mirror.co/showroom"
    session = SgRequests()
    r = session.get(page_url)

    tree = html.fromstring(r.text)
    block = "".join(tree.xpath("//@data-nodes")).replace("/n", "").strip()
    block = block.split('"more_locations":')[1].split(',"locations_filter"')[0]

    js = json.loads(block)

    for j in js:

        ad = "".join(j.get("location")).split("\r\n")
        adr = " ".join(ad).replace("United States", "").replace('"', "").strip()
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = j.get("country") or "US"
        location_name = "".join(j.get("title"))
        if location_name.find("MIRROR at lululemon 29th St, Boulder") != -1:
            street_address = "29th St"
        if location_name.find("MIRROR at lululemon Tysons Corner") != -1:
            street_address = "8066 Tysons Corner Center"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("hours")).replace("\n", "").replace("\r", " ").strip()
        )
        if hours_of_operation.find("BY") != -1:
            hours_of_operation = hours_of_operation.split("ONLY")[1].strip()
        if hours_of_operation.find("See") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("COMING") != -1:
            hours_of_operation = "Coming Soon"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.mirror.co"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
