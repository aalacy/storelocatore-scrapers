import re

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var stations =')]/text()"))
    text = text.split("var stations =")[1].split("];")[0].strip()[:-1] + "]"
    divs = eval(text)

    for d in divs:
        longitude = d.pop()
        latitude = d.pop()
        source = d.pop()
        root = html.fromstring(source)
        location_name = "".join(root.xpath(".//strong/text()")).strip()
        line = root.xpath(".//p//text()")
        line = list(filter(None, [li.replace("\xa0", " ").strip() for li in line]))

        street_address = line.pop(0)
        zc = line.pop()
        postal = "".join(regex.findall(zc))
        city = zc.replace(postal, "").strip()
        country_code = "PL"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    regex = re.compile(r"\d{2}-\d{3}")
    locator_domain = "http://www.qgaz.pl/"
    page_url = "http://www.qgaz.pl/mapa-stacji-paliw/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
