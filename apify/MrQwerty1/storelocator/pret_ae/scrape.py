from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pret.ae/en-ae/find-us"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='map-holder']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='row']//h3[not(@class)]/text()")
        ).strip()
        street_address = ""
        latitude, longitude = "".join(
            d.xpath(".//div[@data-position]/@data-position")
        ).split(",")

        _tmp = []
        li = d.xpath(".//h3/following-sibling::p")
        for l in li:
            line = " ".join(",".join(l.xpath("./text()")).split())
            if "24 hours" in line:
                _tmp.append("24 hours")
                break
            if "floor" in line:
                line = line.split(",")[-1]
            _tmp.append(line)

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city="Dubai",
            country_code="AE",
            latitude=latitude.strip(),
            longitude=longitude.strip(),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pret.ae/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
