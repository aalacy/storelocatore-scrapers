from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burger-king.ch/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "X-Session-Id": "b8f828a1-aad6-4e12-950d-45f420992f9f",
        "x-user-datetime": "2021-08-21T13:54:47+03:00",
        "x-ui-language": "en",
        "x-ui-region": "CH",
        "Origin": "https://www.burger-king.ch",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = '[{"operationName":"GetRestaurants","variables":{"input":{"filter":"NEARBY","coordinates":{"userLat":46.9479739,"userLng":7.4474468,"searchRadius":1500000},"first":200,"status":"OPEN"}},"query":"query GetRestaurants($input: RestaurantsInput) {\\n restaurants(input: $input) {\\n pageInfo {\\n hasNextPage\\n endCursor\\n __typename\\n }\\n totalCount\\n nodes {\\n ...RestaurantNodeFragment\\n __typename\\n }\\n __typename\\n }\\n}\\n\\nfragment RestaurantNodeFragment on RestaurantNode {\\n _id\\n storeId\\n isAvailable\\n posVendor\\n chaseMerchantId\\n curbsideHours {\\n ...OperatingHoursFragment\\n __typename\\n }\\n deliveryHours {\\n ...OperatingHoursFragment\\n __typename\\n }\\n diningRoomHours {\\n ...OperatingHoursFragment\\n __typename\\n }\\n distanceInMiles\\n drinkStationType\\n driveThruHours {\\n ...OperatingHoursFragment\\n __typename\\n }\\n driveThruLaneType\\n email\\n environment\\n franchiseGroupId\\n franchiseGroupName\\n frontCounterClosed\\n hasBreakfast\\n hasBurgersForBreakfast\\n hasCatering\\n hasCurbside\\n hasDelivery\\n hasDineIn\\n hasDriveThru\\n hasMobileOrdering\\n hasParking\\n hasPlayground\\n hasTakeOut\\n hasWifi\\n id\\n isDarkKitchen\\n isFavorite\\n isRecent\\n latitude\\n longitude\\n mobileOrderingStatus\\n name\\n number\\n parkingType\\n phoneNumber\\n physicalAddress {\\n address1\\n address2\\n city\\n country\\n postalCode\\n stateProvince\\n stateProvinceShort\\n __typename\\n }\\n playgroundType\\n pos {\\n vendor\\n __typename\\n }\\n posRestaurantId\\n restaurantImage {\\n asset {\\n _id\\n metadata {\\n lqip\\n palette {\\n dominant {\\n background\\n foreground\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n crop {\\n top\\n bottom\\n left\\n right\\n __typename\\n }\\n hotspot {\\n height\\n width\\n x\\n y\\n __typename\\n }\\n __typename\\n }\\n restaurantPosData {\\n _id\\n __typename\\n }\\n status\\n vatNumber\\n __typename\\n}\\n\\nfragment OperatingHoursFragment on OperatingHours {\\n friClose\\n friOpen\\n monClose\\n monOpen\\n satClose\\n satOpen\\n sunClose\\n sunOpen\\n thrClose\\n thrOpen\\n tueClose\\n tueOpen\\n wedClose\\n wedOpen\\n __typename\\n}\\n"}]'

    r = session.post(
        "https://use1-prod-bk.rbictg.com/graphql", headers=headers, data=data
    )

    js = r.json()[0]["data"]["restaurants"]["nodes"]
    for j in js:

        a = j.get("physicalAddress")
        page_url = f"https://www.burger-king.ch/store-locator/store/{j.get('_id')}"
        location_name = j.get("name")
        location_type = "restaurant"
        street_address = f"{a.get('address1')} {a.get('address2')}".strip()
        state = a.get("stateProvince") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("country")
        city = a.get("city") or "<MISSING>"
        store_number = "".join(j.get("_id")).split("_")[1].strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = "".join(j.get("phoneNumber")) or "<MISSING>"
        if phone.find("E+") != -1:
            phone = "<MISSING>"
        h = j.get("diningRoomHours")
        hours_of_operation = f"Monday {h.get('monOpen')} - {h.get('monClose')} Tuesday {h.get('tueOpen')} - {h.get('tueClose')} Wednesday {h.get('wedOpen')} - {h.get('wedClose')} Thursday {h.get('thrOpen')} - {h.get('thrClose')} Friday {h.get('friOpen')} - {h.get('friClose')} Saturday {h.get('satOpen')} - {h.get('satClose')} Sunday {h.get('sunOpen')} - {h.get('sunClose')}"
        if hours_of_operation.find("None - None ") != -1:
            hours_of_operation = "Closed"

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
