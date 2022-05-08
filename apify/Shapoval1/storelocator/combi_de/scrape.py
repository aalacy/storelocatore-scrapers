import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.combi.de"
    api_url = "https://www.combi.de/unseremaerkte/marktsuche"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "var marketsData = ")]/text()'))
        .split("var marketsData = ")[1]
        .strip()
    )
    js_block = "".join(js_block[:-1])
    js = json.loads(js_block)
    for j in js:

        slug = j.get("url")
        page_url = f"https://www.combi.de{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "DE"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("geo").get("lat") or "<MISSING>"
        longitude = j.get("geo").get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("openingHoursJs")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        if hours:
            for d in days:
                day = d
                try:
                    opens = hours.get(f"{d}")[0].get("opens")
                    closes = hours.get(f"{d}")[0].get("closes")
                except:
                    opens, closes = "Closed", "Closed"
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace("Closed - Closed", "Closed").strip()
            )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
