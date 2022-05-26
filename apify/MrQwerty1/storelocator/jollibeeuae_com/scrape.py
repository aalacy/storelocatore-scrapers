from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[div/h4]")

    for d in divs:
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        line = d.xpath("./following-sibling::div[1]//p[1]//text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        city = line.pop()
        if ", " in city:
            city = city.split(", ")[-1]

        street_address = ", ".join(line)
        country_code = "AE"

        _tmp = []
        hours = d.xpath("./following-sibling::div[1]//p/strong")
        for h in hours:
            day = "".join(h.xpath(".//text()")).strip()
            inter = (
                "".join(h.xpath("./following-sibling::text()[1]"))
                .split(" : ")[-1]
                .strip()
            )
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://jollibeeuae.com/"
    page_url = "https://jollibeeuae.com/find-us/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
