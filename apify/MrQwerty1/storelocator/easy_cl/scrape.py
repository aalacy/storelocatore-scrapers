from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//button[.//p]/following-sibling::div[.//a]")

    for d in divs:
        location_name = city = "".join(d.xpath("./div[1]//text()")).strip()
        state = "".join(d.xpath("./preceding-sibling::button//text()")).strip()
        country_code = "CL"
        text = "".join(d.xpath(".//a/@href"))
        if "ll=" in text:
            latitude, longitude = text.split("ll=")[1].split("&")[0].split(",")
        elif "/@" in text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        else:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        lunes = "".join(d.xpath("./div[2]//p/text()")).replace("|", "").strip()
        if lunes:
            _tmp.append(f"Lunes a sábado: {lunes}")

        domingo = "".join(d.xpath("./div[3]//p/text()")).replace("|", "").strip()
        if lunes:
            _tmp.append(f"Domingo y Festivos: {domingo}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            city=city,
            state=state,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.easy.cl/"
    page_url = "https://www.easy.cl/tiendas"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
