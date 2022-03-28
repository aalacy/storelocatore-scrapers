import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//span[contains(text(), 'Hours')]/following-sibling::span//p/text()"
    )
    hours = " ".join("".join(hours).split())
    return hours


def fetch_data(sgw: SgWriter):
    api = "https://suncountrycleaners.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'map_options')]/text()"))
    text = text.split('"places":')[1].split("]}],")[0] + "]}]"
    js = json.loads(text)

    for j in js:
        location_name = j.get("title")
        source = j.get("content") or "<html></html>"
        root = html.fromstring(source)
        slug = "".join(root.xpath("//a/@href")).replace("..", "")
        page_url = f"https://suncountrycleaners.com{slug}"
        street_address = j.get("address") or ""
        if "," in street_address:
            street_address = street_address.split(",")[0].strip()
        store_number = j.get("id")
        j = j.get("location") or {}
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        try:
            phone = j["extra_fields"]["wsl_phone"]
        except KeyError:
            phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = get_hours(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://suncountrycleaners.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
