from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://papajohns.by/minsk/stores"
    api = (
        "https://api.papajohns.by/page/get?lang=ru&city_id=1&platform=web&alias=stores"
    )
    r = session.get(api)
    source = r.json()["body"]
    tree = html.fromstring(source)
    adr = []
    contact = []
    for t in tree.xpath("//text()"):
        if "Юридический" in t:
            adr.append(t)
        if "телефон" in t:
            contact.append(t)

    for a, c in zip(adr, contact):
        location_name = a.split("Юридический адрес:")[1].split(",")[0].strip()
        postal = a.split(",")[1].strip()
        city = a.split(",")[2].replace("г.", "").strip()
        street_address = ",".join(a.split(",")[3:])
        phone = c.split(":")[1].split("с")[0].strip()
        hours = c.split("с")[1].split("по")[0].replace("до", "-")
        hours_of_operation = f"Mon-Fri: {hours}"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="BY",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://papajohns.by/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
