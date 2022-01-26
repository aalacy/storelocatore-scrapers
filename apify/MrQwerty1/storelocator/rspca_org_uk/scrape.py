import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, _zip):
    adr = parse_address(International_Parser(), line, postcode=_zip)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""

    return street_address, city


def get_cookie():
    r = session.get(api)
    return r.cookies.get("JSESSIONID")


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )
    for _zip in search:
        for i in range(1, 5):
            data = {
                "postcode": _zip,
                "Search": "Find",
                "estabTypeFilterGroupId": str(i),
                "servTypeFilterGroupId": "0",
            }
            if i == 1:
                location_type = "Animal centre"
            elif i == 2:
                location_type = "Shop"
            elif i == 3:
                location_type = "Pet hospital/clinic"
            else:
                location_type = "Wildlife centre"
            r = session.post(api, cookies=cookies, data=data)
            tree = html.fromstring(r.text)
            text = "".join(
                tree.xpath("//script[contains(text(), 'entriesOnMap')]/text()")
            )
            text = text.split('"entriesOnMap":')[1].split("});")[0]
            js = json.loads(text)

            for j in js:
                location_name = j.get("name")
                postal = j.get("postcode")
                latitude = j.get("latitude") or ""
                longitude = j.get("longitude") or ""
                if str(latitude) == "0.0":
                    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
                store_number = j.get("id")
                source = j.get("infoBoxDetail") or "<html></html>"
                root = html.fromstring(source)
                slug = "".join(root.xpath("//a[@class='themeActionButton']/@href"))
                page_url = f"https://www.rspca.org.uk{slug}"
                raw_address = " ".join(
                    " ".join(
                        root.xpath("//div[@class='addressBlock']/span/text()")
                    ).split()
                )
                street_address, city = get_international(raw_address, postal)
                try:
                    phone = root.xpath("//a[contains(@href, 'tel:')]/text()")[0].strip()
                    if "@" in phone or "not" in phone:
                        raise IndexError
                    if "o" in phone:
                        phone = phone.split("o")[0].strip()
                except IndexError:
                    phone = SgRecord.MISSING

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=postal,
                    country_code="GB",
                    location_type=location_type,
                    store_number=store_number,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rspca.org.uk/"
    api = "https://www.rspca.org.uk/whatwedo/yourlocal?p_p_id=iyaSearch_WAR_ptlIYAPortlets&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view"

    cookies = {
        "JSESSIONID": get_cookie(),
    }

    params = (
        ("p_p_id", "iyaSearch_WAR_ptlIYAPortlets"),
        ("p_p_lifecycle", "1"),
        ("p_p_state", "normal"),
        ("p_p_mode", "view"),
    )

    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_TYPE}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
