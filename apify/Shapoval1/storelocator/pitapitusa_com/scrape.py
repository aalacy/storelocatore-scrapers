import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("dayOfWeek")
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{days} {opens} - {closes}"
        if opens == closes:
            line = f"{days} - Closed"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pitapitusa.com/"
    api_url = "https://locations.pitapitusa.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url == "https://locations.pitapitusa.com/index.html":
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        js = json.loads(jsblock)

        location_name = js.get("name") or "<MISSING>"
        location_type = "Restaurant"
        street_address = js.get("address").get("streetAddress") or "<MISSING>"
        state = js.get("address").get("addressRegion") or "<MISSING>"
        postal = js.get("address").get("postalCode") or "<MISSING>"
        country_code = "US"
        city = js.get("address").get("addressLocality") or "<MISSING>"
        latitude = js.get("geo").get("latitude") or "<MISSING>"
        longitude = js.get("geo").get("longitude") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        hours = js.get("openingHoursSpecification") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        hours_of_operation = hours_of_operation.replace(
            "None - Closed; None - Closed; None - Closed; None - Closed; None - Closed;",
            "",
        )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
