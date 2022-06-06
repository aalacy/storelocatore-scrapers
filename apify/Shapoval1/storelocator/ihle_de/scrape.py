from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ihle.de/"
    page_url = "https://www.ihle.de/alle-standorte.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@id, "collapse")]/div/p')
    for d in div:

        location_name = "".join(d.xpath("./strong[1]/text()"))
        ad = (
            "".join(d.xpath(".//strong/following-sibling::text()[2]"))
            .replace("\n", "")
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[0].strip()
        country_code = "DE"
        city = " ".join(ad.split(",")[1].split()[1:]).strip()
        if city.find("/") != -1:
            city = city.split("/")[0].strip()
        info = d.xpath(".//strong//following-sibling::text()")
        info = list(filter(None, [a.strip() for a in info]))
        phone = "<MISSING>"
        for i in info:
            if "Telefon" in i:
                phone = str(i).replace("Telefon:", "").strip()
        hours_of_operation = "<MISSING>"
        for i in info:
            if "Mo" in i or "So" in i:
                hours_of_operation = str(i)
        if hours_of_operation.endswith(","):
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
