import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.daveshotchicken.com/"
    api_url = "https://www.daveshotchicken.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h2]")
    for d in div:

        page_url = "https://www.daveshotchicken.com/locations"
        location_name = "".join(d.xpath(".//h2/text()"))
        if "@" in location_name:
            continue
        info = d.xpath(".//h2/following-sibling::p/text()")
        info = list(filter(None, [a.strip() for a in info]))
        tmp = []
        for i in info:
            if "(" in i and "3642" not in i:
                break
            tmp.append(i)
        ad = " ".join(tmp).replace("Midtown:", "").strip()
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        adr = " ".join(info)
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        if postal.isdigit() or state == "TX":
            country_code = "US"
        city = a.city or "<MISSING>"
        ph = re.findall(r"[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}", adr) or "<MISSING>"
        phone = "".join(ph)
        try:
            hours_of_operation = adr.split(f"{phone}")[1].strip()
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Dining Room:") != -1:
            hours_of_operation = hours_of_operation.split("Dining Room:")[1].strip()
        if location_name.find("opening soon") and hours_of_operation == "<MISSING>":
            hours_of_operation = "Coming Soon"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
