import json
import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


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
    if not street_address:
        street_address = line.split(",")[0]
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://cdn.storelocatorwidgets.com/json/305108bbd6b1fed18ddf5701d3977501"
    r = session.get(api, headers=headers)
    text = r.text.replace("slw(", "")[:-1]
    js = json.loads(text)["stores"]

    for j in js:
        location_name = j.get("name")
        d = j.get("data") or {}
        raw_address = d.get("address") or ""
        country = "US"
        if "Sample" in raw_address:
            continue

        if "Canada" in raw_address:
            country = "CA"
            street_address = raw_address.split(", ")[0]
            city = raw_address.split(", ")[1]
            state = raw_address.split(", ")[2].split()[0]
            postal = raw_address.split(", ")[2].replace(state, "").strip()
        else:
            street_address, city, state, postal = get_address(raw_address)

        if ", " in city:
            city = city.split(", ")[-1]
        phone = d.get("phone")
        latitude = d.get("map_lat")
        longitude = d.get("map_lng")
        store_number = j.get("storeid")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            inter = d.get(f"hours_{day}")
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://daisoglobal.com/"
    page_url = "https://www.daisojapan.com/t-storelocator.aspx"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
