from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_hoo(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return ";".join(
        tree.xpath("//strong[contains(text(), 'Hours')]/following-sibling::div/text()")
    )


def fetch_data(sgw: SgWriter):
    api = "https://www.rocklandtrust.com/_/api/branches/0/0/10000"
    r = session.get(api)
    js = r.json()["branches"]

    for j in js:
        text = j.get("description") or "<html></html>"
        text = text.replace("&nbsp;", " ").replace("&amp;", "&")
        tree = html.fromstring(text)
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        page_url = tree.xpath("//a[not(contains(@href, 'mailto'))]/@href")[0]

        location_name = j.get("name") or ""
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("long")

        hours = tree.xpath(
            "//*[contains(text(), ': ') or contains(text(), 'Drive') or contains(text(), 'Teller Hours')]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours = ";".join(hours).replace("\n", "")
        if hours.find("Drive") != -1:
            hours = hours.split("Drive")[0]
        elif hours.find("Teller") != -1:
            hours = hours.split("Teller")[0]
        if "Video" in hours:
            hours = hours.split("Video")[0]
        if ":;" in hours:
            hours = hours.split(":;")[-1]

        hours_of_operation = hours
        if not hours_of_operation:
            hours_of_operation = get_hoo(page_url)
        if hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        row = SgRecord(
            location_name=location_name,
            page_url=page_url,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rocklandtrust.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
