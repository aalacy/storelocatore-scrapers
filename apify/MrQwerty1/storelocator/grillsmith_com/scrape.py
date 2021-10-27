import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//h2[contains(text(), 'Hours')]/following-sibling::p[not(./a)]//text()"
    )
    hours = ";".join(list(filter(None, [h.strip() for h in hours])))
    if "temporarily" in hours.lower():
        hours = "Temporarily Closed"

    lat = "".join(tree.xpath("//div[@data-gmaps-lat]/@data-gmaps-lat"))
    lng = "".join(tree.xpath("//div[@data-gmaps-lng]/@data-gmaps-lng"))

    return lat, lng, hours


def fetch_data(sgw: SgWriter):
    api_url = "https://www.grillsmith.com/location/carrollwood/"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Organization')]/text()"))
    js = json.loads(text)["subOrganization"]

    for j in js:
        a = j.get("address")
        street_address = a.get("streetAddress")
        city = a.get("addressLocality")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = "US"
        page_url = j.get("url")
        location_name = j.get("name")
        phone = j.get("telephone")
        latitude, longitude, hours_of_operation = get_additional(page_url)
        location_type = j.get("@type")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
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
    locator_domain = "https://www.grillsmith.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
