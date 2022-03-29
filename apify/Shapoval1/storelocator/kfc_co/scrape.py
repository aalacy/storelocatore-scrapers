import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.co/"
    page_url = "https://www.kfc.co/nuestras-tiendas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath("//div/@data-maps-collection-value"))
    js = json.loads(div)
    for j in js.values():
        for a in j:

            location_name = a.get("name") or "<MISSING>"
            street_address = a.get("address1") or "<MISSING>"
            country_code = "CO"
            city = "".join(a.get("city")) or "<MISSING>"
            if city.find("/") != -1:
                street_address = city.split("/")[1].strip()
                city = city.split("/")[0].strip()
            if city.find("DIAGONAL SANTANDER") != -1:
                street_address = city.split("DIAGONAL SANTANDER")[1].strip()
                city = "DIAGONAL SANTANDER"
            store_number = a.get("id") or "<MISSING>"
            latitude = a.get("lat") or "<MISSING>"
            longitude = a.get("lng") or "<MISSING>"
            phone = a.get("phone") or "<MISSING>"
            if (
                location_name.find("HELENITA") == -1
                and city == "<MISSING>"
                and location_name.find("ISERRA") == -1
            ):
                city = location_name.split()[1].strip()
            if location_name.find("HELENITA") != -1 and city == "<MISSING>":
                city = location_name

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
