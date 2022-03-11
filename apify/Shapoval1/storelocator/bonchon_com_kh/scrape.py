from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bonchon.com.kh/"
    page_url = "https://www.bonchon.com.kh/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h3/strong]")
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        info = d.xpath(".//p//text()")
        info = list(filter(None, [a.strip() for a in info]))
        ad = "<MISSING>"
        tmp = []
        for i in info:
            if ":" not in i:
                tmp.append(i)
            ad = " ".join(tmp)
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "KH"
        city = a.city or "<MISSING>"
        if "Phnom Penh" in location_name:
            city = "Phnom Penh"
        phone = "<MISSING>"
        for i in info:
            if "Tel" in i:
                phone = "".join(i).replace("Tel:", "").strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/preceding::h1[./strong[text()="Opening Hours"]]/following-sibling::*//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
