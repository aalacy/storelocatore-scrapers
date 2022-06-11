import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import sglog
from tenacity import retry, stop_after_attempt, wait_fixed


def get_token():
    r = session.get("https://www.stinker.com/store-search/", headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='locator-js-extra']/text()"))
    key = text.split('"lkp":"')[1].split('"')[0].strip()

    return key


def get_address(line):
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
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = SgRecord.MISSING
    city = a.get("city")
    if city == "USA":
        city = SgRecord.MISSING
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


@retry(stop=stop_after_attempt(2), wait=wait_fixed(5))
def get_json(api):
    r = session.get(api, headers=headers)
    logger.info(f"{api}: {r}")
    js = r.json()["locations"]

    return js


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=10,
        max_search_distance_miles=10000,
    )
    for lat, lng in search:
        api = f"https://www.stinker.com/system/wp-admin/admin-ajax.php?action=lookupLocations&lkp={token}&lat={lat}&lng={lng}"
        try:
            js = get_json(api)
        except Exception as e:
            logger.info(f"{api}: {e}")
            continue

        for j in js:
            loc = j.get("latLng")
            latitude = loc.get("latitude")
            longitude = loc.get("longitude")
            search.found_location_at(latitude, longitude)
            j = j.get("popupInfo")

            raw_address = j.get("location")
            street_address, city, state, postal = get_address(raw_address)
            location_name = j.get("title").replace("&#038;", "&")
            store_number = location_name.split()[0].replace("#", "")
            if not store_number.isdigit():
                store_number = SgRecord.MISSING
            phone = j["otherInfo"]["phone"]

            hours = j.get("content")
            try:
                hours_of_operation = (
                    hours.split("Hours:")[1]
                    .replace("pm ", "pm; ")
                    .split("</p>\n")[0]
                    .strip()
                )
                if "<" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("<")[0].strip()
            except IndexError:
                hours_of_operation = SgRecord.MISSING

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
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://stinker.com/"
    page_url = "https://www.stinker.com/store-search/"
    logger = sglog.SgLogSetup().get_logger(logger_name="stinker.com")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
    }
    token = get_token()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
