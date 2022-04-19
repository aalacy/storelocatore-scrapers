from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[contains(@class, 'day-hours')]")
    for h in hours:
        _tmp.append(" ".join(" ".join(h.xpath(".//text()")).split()))

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://api.carstar.ca/api/stores/"
    r = session.get(api, headers=headers)
    js = r.json()["message"]["stores"]

    for j in js:
        location_name = j.get("storeName")
        street_address = j.get("streetAddress1")
        city = j.get("locationCity")
        state = j.get("locationState")
        postal = j.get("locationPostalCode")
        country_code = "CA"
        store_number = j.get("storeId")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("Type")
        page_url = f"{locator_domain}en/locations/{state.lower()}/{j.get('locationCitySlug')}/carstar-{store_number}/"
        try:
            hours_of_operation = get_hoo(page_url)
        except:
            hours_of_operation = SgRecord.MISSING

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
            location_type=location_type,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.carstar.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
