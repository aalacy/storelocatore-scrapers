import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def get_coords(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    if "/@" in text:
        return text.split("/@")[1].split(",")[:2]
    return SgRecord.MISSING, SgRecord.MISSING


def get_street(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    adr1 = a.get("address1") or ""
    adr2 = a.get("address2") or ""
    street_address = f"{adr1} {adr2}".strip()

    return street_address


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )
    for _zip in search:
        api = f"https://www.alwaysbestcare.com/wp-json/ral/v1/location/offices?q={_zip}"
        r = session.get(api, headers=headers)
        js = r.json()["features"]

        for j in js:
            p = j.get("properties") or {}
            adr = p.get("address") or ""
            adr = adr.replace("<br />", " ")
            street_address = get_street(adr)
            city = p.get("city") or ""
            if "Point Mugu Nawc" in city:
                continue
            state = p.get("state")
            postal = p.get("zip")
            country_code = "US"
            store_number = p.get("storeid")
            location_name = p.get("name")
            page_url = p.get("url")
            phone = p.get("phone")

            g = j.get("geometry") or {}
            longitude, latitude = g.get("coordinates") or (
                SgRecord.MISSING,
                SgRecord.MISSING,
            )
            if latitude == SgRecord.MISSING or latitude == 0:
                try:
                    latitude, longitude = get_coords(page_url)
                except:
                    pass

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
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.alwaysbestcare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
