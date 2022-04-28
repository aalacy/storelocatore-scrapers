from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='link-content-pad']")

    for d in divs:
        location_name = raw_address = "".join(d.xpath(".//h4/text()")).strip()
        if location_name.endswith(","):
            location_name = raw_address = location_name[:-1]

        city, street_address = raw_address.split(", ")
        country_code = "SK"

        line = d.xpath("./p/text()")
        line = list(filter(None, [li.strip() for li in line]))
        if "@" in line[-1]:
            line.pop()

        phone = SgRecord.MISSING
        if "Tel" in line[-1]:
            phone = (
                line.pop().replace("Tel", "").replace(".", "").replace(":", "").strip()
            )
            if "," in phone:
                phone = phone.split(",")[0].strip()

        _tmp = []
        write = False
        for li in line:
            if "hodiny" in li.lower():
                write = True

            if write:
                if "25.12" in li:
                    continue
                if "non-stop" in li.lower():
                    _tmp.append("24/7")
                    continue
                _tmp.append(li)

        hours_of_operation = ";".join(_tmp)
        hours_of_operation = hours_of_operation.split("hodiny:")[-1].strip()
        if hours_of_operation.startswith(";"):
            hours_of_operation = hours_of_operation[1:]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            phone=phone,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "hhttps://www.ftcgulf.sk/"
    page_url = "https://www.ftcgulf.sk/products-services/fuel/siet-cerpacich-stanic/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
