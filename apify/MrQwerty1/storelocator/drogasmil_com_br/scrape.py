from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='vtex-rich-text-0-x-wrapper vtex-rich-text-0-x-wrapper--infocard-text']/*"
    )
    state = SgRecord.MISSING

    for d in divs:
        if d.xpath("name()") == "h3":
            state = "".join(d.xpath("./text()")).strip()
            continue

        location_name = "".join(d.xpath("./span/text()")).strip()

        _tmp = []
        line = d.xpath("./text()")
        for li in line:
            li = li.replace("Tel:", "").replace("Tel", "").replace("*", "").strip()
            if not li:
                continue
            if li.startswith("-"):
                li = li[1:].strip()
            if li.endswith("-"):
                li = li[:-1].strip()
            _tmp.append(li)

        t = " - ".join(_tmp)
        if not t:
            city = location_name
            street_address, postal = SgRecord.MISSING, SgRecord.MISSING
        else:
            postal = t.split(":")[-1].strip()
            city = location_name.split(" - ")[0].strip()
            adr1 = location_name.split(" - ")[-1].strip()
            adr2 = ""
            if " - " in t:
                adr2 = t.split(" - ")[0].replace(".", "").strip()
            street_address = " ".join(f"{adr1} {adr2}".replace("*", "").split())

        phone = "".join(d.xpath(".//a/text()")).replace("Tel", "").strip()
        country_code = "BR"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            phone=phone,
            country_code=country_code,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.drogasmil.com.br/"
    page_url = "https://www.drogasmil.com.br/lojas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
