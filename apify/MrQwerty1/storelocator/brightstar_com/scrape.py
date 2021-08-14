from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def fetch_data(sgw: SgWriter):
    page_url = "https://www.brightstar.com/contact-us/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-xs-12 col-md-12']/article")

    for d in divs:
        location_name = "".join(d.xpath("./h2/text()")).strip()
        phone = SgRecord.MISSING

        _tmp = []
        lines = d.xpath("./p/text()")
        black_list = ["Brightstar", "E-mail:", "Website", "普", "@brightstar.com"]
        for line in lines:
            skip = False
            for black in black_list:
                if black in line:
                    skip = True
                    break
            if skip:
                continue
            _tmp.append(line.strip())

        if not _tmp:
            continue

        p = _tmp[-1].lower()
        if "china" in p or "kista" in p or "oslo" in p:
            pass
        elif "phone" in p or "tel" in p or p[0].isdigit() or p[0] == "(":
            phone = _tmp.pop()
            if ":" in phone:
                phone = phone.split(":")[-1].strip()
            if "|" in phone:
                phone = phone.split("|")[-1].strip()

        line = ", ".join(_tmp)
        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or SgRecord.MISSING
        )

        city = adr.city or SgRecord.MISSING
        if len(city) < 3:
            city = line.split(",")[-2].strip()

        if " CP " in city:
            city = city.split(" CP")[0].strip()

        state = adr.state or SgRecord.MISSING
        postal = adr.postcode or SgRecord.MISSING
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            locator_domain=locator_domain,
            hours_of_operation=SgRecord.MISSING,
            raw_address=line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.brightstar.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
