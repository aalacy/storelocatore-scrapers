from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    phone = (
        "".join(tree.xpath("//a[@class='brand-phone']/text()"))
        .replace("phone-number", "")
        .strip()
    )
    if not phone:
        phone = "".join(
            tree.xpath("//a[contains(text(), 'Call Now at')]/@href")
        ).replace("tel:", "")

    _tmp = []
    hours = tree.xpath("//div[@class='working-hours']/div")
    for h in hours:
        day = "".join(h.xpath("./div[1]//text()")).strip()
        inter = "".join(h.xpath("./div[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return phone, ";".join(_tmp)


def fetch_data(coords, country_code, sgw):
    lat, lng = coords
    if country_code == "us":
        _filter = "283"
    else:
        _filter = "281"

    url = f"https://www.novusglass.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&filter={_filter}&autoload=1"
    r = session.get(url, headers=headers)

    for j in r.json():
        slug = j.get("store") or ""
        slug = (
            slug.replace("&#8211;", "–")
            .replace(" ", "-")
            .replace("&#8217;", "'")
            .lower()
        )
        page_url = f"https://www.novusglass.com/en-{country_code}/shop/{slug}/"
        street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
        if "NULL" in street_address or "MOBILE" in street_address:
            street_address = SgRecord.MISSING
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip") or ""
        if "NULL" in postal:
            postal = SgRecord.MISSING
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_name = f"NOVUS GLASS OF {city}"

        try:
            phone, hours_of_operation = get_additional(page_url)
        except:
            phone, hours_of_operation = SgRecord.MISSING, SgRecord.MISSING

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
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.novusglass.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    }

    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = [SearchableCountries.USA, SearchableCountries.CANADA]
        search = DynamicGeoSearch(
            country_codes=countries, expected_search_radius_miles=200
        )
        for coord in search:
            fetch_data(coord, search.current_country(), writer)
