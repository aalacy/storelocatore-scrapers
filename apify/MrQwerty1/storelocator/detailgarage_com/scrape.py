import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.detailgarage.com/s/detailgarage/storelocator?showMap=true&horizontalView=true&isForm=true"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    js = json.loads("".join(tree.xpath("//div[@data-locations]/@data-locations")))

    for j in js:
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        text = j.get("infoWindowHtml") or "<html></html>"
        root = html.fromstring(text)
        store_number = "".join(root.xpath("//div[@data-store-id]/@data-store-id"))
        page_url = f"https://www.detailgarage.com/{store_number}.html"
        line = root.xpath("//div[contains(@class, 'store-address')]//text()")
        line = list(filter(None, [l.strip() for l in line]))
        postal = line.pop()
        state = line.pop()
        city = line.pop().replace(",", "")
        street_address = ", ".join(line)
        country_code = "US"
        if len(postal) > 5:
            country_code = "CA"
        phone = "".join(root.xpath("//a[contains(@href, 'tel:')]/@href")).replace(
            "tel:", ""
        )

        _tmp = []
        hours = root.xpath("//div[contains(@class, 'store-hours')]/p[./strong or ./b]")
        for h in hours:
            line = " ".join(" ".join(h.xpath(".//text()")).split()).strip()
            if line:
                _tmp.append(line)

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.detailgarage.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
