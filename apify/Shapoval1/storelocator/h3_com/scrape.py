from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.h3.com/"
    api_url = "https://www.h3.com/pt/onde.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("var features = ")[1]
        .split(";")[0]
        .split("}")
    )
    for d in div[:-1]:

        page_url = "https://www.h3.com/pt/onde.html"
        content = d.split("content:")[1].replace("'", "").replace("+", "").strip()
        a = html.fromstring(content)
        location_name = "".join(a.xpath("//h2/text()"))
        ad = "".join(a.xpath("//p[1]//text()"))
        adr = ad.split(",")[-1].replace("31 A -", "").replace(" - ", "-").strip()
        street_address = ad.split(f"{adr}")[0].replace("-", "").replace(",", "").strip()
        postal = adr.split()[0].strip()
        country_code = "PT"
        city = " ".join(adr.split()[1:]).strip()
        latitude = d.split("LatLng(")[1].split(",")[0].strip()
        longitude = d.split("LatLng(")[1].split(",")[1].split(")")[0].strip()
        hours_of_operation = (
            "".join(a.xpath("//p[2]//text()")).replace("Horário:", "").strip()
        )

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
