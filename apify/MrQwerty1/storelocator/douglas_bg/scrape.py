import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://douglas.bg/stores/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    coords = dict()
    text = "".join(tree.xpath("//script[contains(text(), 'var shopsData =')]/text()"))
    text = text.split("var shopsData =")[1].split("}];")[0] + "}]"
    js = json.loads(text)
    for j in js:
        _id = j.get("id")
        lat = j.get("latitude")
        lng = j.get("longitude")
        coords[_id] = (lat, lng)

    divs = tree.xpath("//div[@class='shop-item douglas']")

    for d in divs:
        store_number = "".join(d.xpath("./@data-shop"))
        location_name = "".join(d.xpath(".//span[@class='name']/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='link']/@href"))
        raw_address = "".join(d.xpath(".//span[@class='address']/text()")).strip()
        line = raw_address.split(", ")
        city = line.pop(0)
        street_address, postal = SgRecord.MISSING, SgRecord.MISSING
        for li in line:
            li = li.strip()
            if li.startswith("ул") or li.startswith("бул"):
                street_address = li
            if li[0].isdigit() and li[-1].isdigit():
                postal = li

        country_code = "BG"
        phone = "".join(d.xpath(".//a[@class='phone']/text()")).strip()
        latitude, longitude = coords.get(store_number) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        hours_of_operation = (
            "".join(d.xpath(".//span[@class='working-time']/text()"))
            .replace("от", "")
            .replace("до", "-")
            .strip()
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://douglas.bg/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
