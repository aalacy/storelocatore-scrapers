import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://dominocstores.com/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    part = dict()
    markers = tree.xpath("//div[@data-x-element='map_google_marker']/@data-x-params")
    for m in markers:
        j = json.loads(m)
        root = html.fromstring(j.get("content"))
        _id = "".join(root.xpath("./a[1]/text()")).split("#")[-1]
        lat = j.get("lat") or SgRecord.MISSING
        lng = j.get("lng") or SgRecord.MISSING
        phone = (
            "".join(root.xpath("./a[contains(@href, 'tel')]/text()")).strip()
            or SgRecord.MISSING
        )
        hoo = "".join(root.xpath("./text()")).strip() or SgRecord.MISSING
        part[_id] = {"lat": lat, "lng": lng, "phone": phone, "hoo": hoo}

    divs = tree.xpath("//div[contains(@class, 'x-column x-sm x-1-4') and ./h3]")

    for d in divs:
        location_name = "".join(d.xpath(".//a/text()")).strip()
        page_url = "https://dominocstores.com/locations" + d.xpath(".//a/@href")[0]
        line = d.xpath(".//div/p//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = "".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = location_name.split("#")[-1]
        phone = part[store_number].get("phone")
        latitude = part[store_number].get("lat")
        longitude = part[store_number].get("lng")
        hours_of_operation = part[store_number].get("hoo")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
    locator_domain = "https://dominocstores.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
