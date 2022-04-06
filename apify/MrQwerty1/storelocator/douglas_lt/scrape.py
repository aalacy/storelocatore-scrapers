import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.douglas.lt/parduotuves/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'store_markers')]/text()"))
    text = text.split("store_markers =")[1].split("]};")[0] + "]}"
    coords = json.loads(text)
    divs = tree.xpath("//div[contains(@id, 'item')]")

    for d in divs:
        store_number = "".join(d.xpath("./@id")).replace("item", "")
        location_name = "".join(d.xpath(".//div[@class='title']/text()")).strip()
        line = d.xpath(".//div[@class='contacts']/text()")
        line = list(filter(None, [li.strip() for li in line]))
        if "atsiėmimas" in line[0]:
            line.pop(0)

        raw_address = line.pop(0)
        street_address, city, postal = raw_address.split(",")
        postal = postal.replace("LT-", "").strip()
        country_code = "LT"

        phone = SgRecord.MISSING
        for li in line:
            if "Tel" in li:
                phone = (
                    line.pop(line.index(li)).replace("Tel", "").replace(".", "").strip()
                )
                break

        latitude, longitude = coords.get(store_number) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        if "@" in line[0]:
            line.pop(0)

        hours = ";".join(line)
        hours = (
            hours.replace("V II", "VII")
            .replace("VII", "Sun")
            .replace("VI", "Sat")
            .replace("V", "Fri")
            .replace("I", "Mon")
        )
        hours_of_operation = " ".join(hours.split()).replace(" ;", "")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.douglas.lt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
