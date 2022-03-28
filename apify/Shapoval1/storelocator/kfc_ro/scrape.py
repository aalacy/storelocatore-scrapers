import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.ro/"
    api_url = "https://www.kfc.ro/restaurante"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "restaurants:")]/text()'))
        .split("restaurants:")[1]
        .split("cities: [],")[0]
        .replace("}],", "}]")
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:

        page_url = j.get("url")
        location_name = j.get("denumire")
        ad = "".join(j.get("adresa"))
        street_address = " ".join(ad.split(",")[1:]).strip()
        country_code = "RO"
        city = j.get("oras")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("mobil") or "<MISSING>"
        hours_of_operation = "".join(j.get("program")).replace("\n", " ").strip()
        if hours_of_operation.find("Program") != -1:
            hours_of_operation = hours_of_operation.split("Program")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
