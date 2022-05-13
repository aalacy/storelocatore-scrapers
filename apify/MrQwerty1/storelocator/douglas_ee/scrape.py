import json
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//script[contains(text(), 'store_markers')]/text()"))
    text = text.split("store_markers =")[1].split(";")[0]
    coords = json.loads(text)

    text = "".join(tree.xpath("//script[contains(text(), 'var tooltips =')]/text()"))
    text = text.split("var tooltips =")[1].split(";")[0]
    js = json.loads(text)

    for store_number, source in js.items():
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        line = d.xpath("./div/text()")
        line = list(filter(None, [li.strip() for li in line]))
        index = 0
        for li in line:
            if "@" in li:
                break
            index += 1

        raw_address = line[index - 1]
        phone = line.pop()
        adr = raw_address.split(", ")
        street_address = adr.pop(0)
        zc = adr.pop(0)
        postal = "".join(re.findall(r"\d{5}", zc))
        city = zc.replace(postal, "")
        country_code = "EE"

        latitude, longitude = coords.get(store_number) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )
        hours = ";".join(line[index + 1 :])
        hours_of_operation = (
            hours.replace("VII", "Sunday")
            .replace("VI", "Saturday")
            .replace("V", "Friday")
            .replace("I", "Monday")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.douglas.ee/"
    page_url = "https://www.douglas.ee/ee/kontaktid/poed/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
