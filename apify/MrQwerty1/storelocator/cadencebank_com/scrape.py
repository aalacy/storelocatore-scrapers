from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(url):
    _tmp = []
    r = session.get(url)
    tree = html.fromstring(r.text)
    hoo = tree.xpath(
        "//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'branch hours')]/following-sibling::p//text()"
    )
    if not hoo:
        hoo = tree.xpath(
            "//h3[contains(text(), 'Location Hours')]/following-sibling::p//text()"
        )
    for h in hoo:
        if "Extended" in h:
            break
        if not h.strip() or "hours" in h.lower() or "*" in h:
            continue

        _tmp.append(h.strip())

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api_url = "https://cadencebank.com/find-us"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locations.push(')]/text()"))
    divs = text.split("locations.push(")[1:]

    for d in divs:
        _id = d.split("Id :")[1].split('"')[1]
        location_name = d.split("Name:")[1].split('"')[1]
        page_url = "".join(
            tree.xpath(f"//div[@data-id='{_id}']//a[@class='location-link']/@href")
        )

        street_address = d.split("Address:")[1].split('"')[1]
        city = d.split("City:")[1].split('"')[1]
        state = d.split("State:")[1].split('"')[1]
        postal = d.split("ZipCode:")[1].split('"')[1]
        country_code = "US"
        store_number = _id
        phone = d.split("Telephone:")[1].split('"')[1]
        latitude = d.split("Latitude:")[1].split("}")[0].split(",")[0].strip()
        longitude = d.split("Longitude:")[1].split(",")[0].strip()

        location_type = (
            "".join(tree.xpath(f"//div[@data-id='{_id}']//div[@class='types']/text()"))
            .replace(" | ", ", ")
            .strip()
        )
        if location_type == "ATM" or not location_type:
            continue

        hours_of_operation = get_hours(page_url)
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://cadencebank.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
