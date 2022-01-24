import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.theproteinbar.com/restaurants/"

    r = session.get(api)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locations:')]/text()"))
    text = text.split("locations:")[1].split("apiKey")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        if len(state) > 2:
            continue
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id")
        page_url = f'https://www.theproteinbar.com{j.get("url")}'
        location_name = j.get("name")
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"

        _tmp = []
        text = j.get("hours") or "<html></html>"
        root = html.fromstring(text)
        days = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/text()")
        times = root.xpath("//p[.//*[contains(text(), 'Mon')]]/text()")
        if not times:
            days = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/strong/text()")
            times = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/text()")

        days = list(filter(None, [d.replace("\xa0", "").strip() for d in days]))
        for d, t in zip(days, times):
            _tmp.append(f"{d.strip()}: {t.strip()}")

        hours_of_operation = ";".join(_tmp).replace("Sat: Fri", "Sat: Closed;Fri")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.theproteinbar.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
