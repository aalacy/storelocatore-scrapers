from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_types():
    types = dict()
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)
    slugs = set(tree.xpath("//a[text()='FULL SERVICE']/following-sibling::ul//a/@href"))
    for slug in slugs:
        types[slug] = "Full Service"

    return types


def fetch_data(sgw: SgWriter):
    types = get_types()
    api = "https://personaltouchcarwashes.com/wp-content/plugins/leaflet-maps-marker/leaflet-geojson.php?layer=1&full=no&full_icon_url=no"
    r = session.get(api, headers=headers)
    js = r.json()["features"]

    for j in js:
        try:
            longitude, latitude = j["geometry"]["coordinates"]
        except KeyError:
            longitude, latitude = SgRecord.MISSING, SgRecord.MISSING
        j = j.get("properties") or {}
        location_name = j.get("markername") or ""
        text = j.get("text") or "<html></html>"
        d = html.fromstring(text)
        slug = location_name.lower().replace(" ", "-")
        if "---" in slug:
            slug = slug.split("---")[0]
        page_url = f"{locator_domain}{slug}/"
        raw_address = "".join(
            d.xpath(".//div[contains(@class, 'item-address')]/span/text()")
        ).strip()
        line = raw_address.split(",")
        street_address = line.pop(0).strip()
        city = line.pop(0).strip()
        sz = line.pop(0).strip()
        state, postal = sz.split()
        phone = "".join(
            d.xpath(".//div[contains(@class, 'item-phone')]//text()")
        ).strip()

        location_type = types.get(page_url) or "Express"
        hours = d.xpath(".//div[contains(@class, 'working-hours')]/span/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            location_type=location_type,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://personaltouchcarwashes.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
