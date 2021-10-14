import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://californiasun.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'mapp.data.push(')]/text()"))
    text = text.split('"pois":')[1].split("}}}]")[0] + "}}}]"
    js = json.loads(text)

    for j in js:
        source = j.get("body") or "<html></html>"
        root = html.fromstring(source)

        location_name = j.get("title")
        slug = "".join(root.xpath("//a[contains(@href, 'locations')]/@href"))
        page_url = f"https://californiasun.com{slug}"

        line = root.xpath("//div[@class='location-address']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        if street_address.endswith(","):
            street_address = street_address[:-1]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = "".join(root.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        latitude = j["point"]["lat"]
        longitude = j["point"]["lng"]
        divs = root.xpath("//div[@class='location-hours']/text()")
        divs = list(filter(None, [d.strip() for d in divs]))
        hours_of_operation = ";".join(divs)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://californiasun.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
