import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.paul-uk.com/find-a-paul"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'storeList')]/text()"))
    text = text.split('"storeList":')[1].split("}},")[0] + "}}"
    js = json.loads(text).items()

    for store_number, j in js:
        source = j.get("info") or "<html>"
        d = html.fromstring(source)
        line = d.xpath(".//div[@class='col-sm-6'][1]//text()")
        line = list(filter(None, [li.strip() for li in line]))
        if "Air" in line[-1]:
            line.pop()

        phone = line.pop()
        postal = line.pop()
        city = line.pop()
        street_address = ", ".join(line)
        if street_address.endswith(","):
            street_address = street_address[:-1]
        country_code = "GB"
        location_name = j.get("title")
        page_url = "".join(
            tree.xpath(
                f"//div[@id='{store_number}']//a[contains(text(), 'info')]/@href"
            )
        )
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours = d.xpath(".//div[@class='col-sm-6'][last()]//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = (
            ";".join(hours).replace(":00:00", ":00").replace(":30:00", ":30")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul-uk.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
