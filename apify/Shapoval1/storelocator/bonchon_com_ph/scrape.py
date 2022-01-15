from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://bonchon.com.ph"
    page_url = "http://bonchon.com.ph/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//table//tr[./td]")
    for d in div:

        location_name = (
            "".join(d.xpath(".//td[1]/text()")).replace("\n", "").strip() or "<MISSING>"
        )
        if location_name == "<MISSING>":
            continue
        ad = "".join(d.xpath(".//td[4]/text()")).replace("\n", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//td[3]/text()")).replace("\n", "").strip() or "<MISSING>"
        )
        country_code = "PH"
        city = (
            "".join(d.xpath(".//td[2]/text()")).replace("\n", "").strip() or "<MISSING>"
        )
        phone = (
            " ".join(d.xpath(".//td[6]/text()")).replace("\n", " ").strip()
            or "<MISSING>"
        )
        try:
            if phone[3] == "-":
                phone = phone.split()[0].strip()
        except:
            phone = phone
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        if phone == "-":
            phone = "<MISSING>"
        if phone.find("  ") != -1:
            phone = phone.split("  ")[0].strip()
        if phone.count(" ") > 1 and phone.count("-") > 1:
            phone = " ".join(phone.split()[:-1])
        hours_of_operation = (
            "".join(d.xpath(".//td[5]/text()"))
            .replace("\n", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
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
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
