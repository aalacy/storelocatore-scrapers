import json
import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


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
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=20
    )
    for lat, lng in search:
        data = {
            "operationName": "stores",
            "variables": {
                "externalId": None,
                "customerId": None,
                "lat": lat,
                "lng": lng,
            },
            "query": "query stores($lat: Float, $lng: Float, $externalId: String, $customerId: ID, $orderTypeId: ID) {  storeSearch(data: {lat: $lat, lng: $lng, externalId: $externalId, customerId: $customerId, orderTypeId: $orderTypeId}) {    lat    lng    address {      address1      city      state      postcode      lat      lng      __typename    }    stores {      id      name      address      distanceToStore      phone      storefrontImage      lat      lng      inDeliveryRange      boundary      status      note      storeType      isPickupOpen      isDeliveryOpen      hours {        type        days {          day          hour          __typename        }        __typename      }      __typename    }    __typename  }}",
        }

        api = "https://api.insomniacookies.com/graphql"
        r = session.post(api, headers=headers, data=json.dumps(data))
        js = r.json()["data"]["storeSearch"]["stores"]

        for j in js:
            location_name = j.get("name")
            raw_address = j.get("address")
            street_address, city, state, postal = get_address(raw_address)
            store_number = j.get("id")
            page_url = f"https://insomniacookies.com/locations/store/{store_number}"
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")

            _tmp = []
            days = []
            hours = j.get("hours")
            for h in hours:
                _type = h.get("type") or ""
                if "Retail" in _type:
                    days = h.get("days")
                    break

            for d in days:
                day = d.get("day")
                hour = d.get("hour")
                if hour.count("Closed") == 2:
                    hour = "Closed"
                _tmp.append(f"{day}: {hour}")

            hours_of_operation = ";".join(_tmp)

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
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://insomniacookies.com/"
    headers = {"content-type": "application/json"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
