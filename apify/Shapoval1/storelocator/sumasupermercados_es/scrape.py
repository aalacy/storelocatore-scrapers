from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sumasupermercados.es/"
    api_url = "https://www.sumasupermercados.es/es/tiendas"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var locations")]/text()'))
        .split("var locations = ")[1]
        .split("];")[0]
        .strip()
    )
    block = div.split("[")
    block = list(filter(None, [a.strip() for a in block]))

    for b in block:
        if not b:
            continue
        b = str(b).replace("&nbsp;", " ")
        page_url = "https://www.sumasupermercados.es/es/tiendas"
        location_name = b.split("<b>")[1].split("</b>")[0].strip()
        ad = b.split("<br>")[1].split("',")[0].strip()
        street_address = " ".join(ad.split(",")[:-2]).strip()
        postal = ad.split(",")[-2].strip()
        if postal == "00000":
            postal = "<MISSING>"
        city = ad.split(",")[-1].strip()
        latitude = b.split("',")[1].split(",")[0].strip()
        longitude = b.split("',")[1].split(",")[1].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
