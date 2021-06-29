import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://bruxie.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Referer": "https://order.online/sl/bruxie--the-original-fried-chicken-and-waffle-sandwich-48317/en-US",
        "content-type": "application/json",
        "X-Experience-Id": "storefront",
        "X-Channel-Id": "marketplace",
        "apollographql-client-name": "@doordash/app-consumer-production",
        "apollographql-client-version": "0.441.0-production",
        "X-CSRFToken": "",
        "Origin": "https://order.online",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    data = '{"operationName":"allBusinessStores","variables":{"businessId":"2554"},"query":"query allBusinessStores($businessId: ID!) {\\n businessInfo(businessId: $businessId) {\\n stores {\\n id\\n name\\n address {\\n id\\n city\\n subpremise\\n printableAddress\\n state\\n street\\n country\\n lat\\n lng\\n shortname\\n zipCode\\n __typename\\n }\\n offersPickup\\n offersDelivery\\n __typename\\n }\\n __typename\\n }\\n}\\n"}'

    r = session.post("https://order.online/graphql", headers=headers, data=data)
    js = r.json()
    for j in js["data"]["businessInfo"]["stores"]:
        a = j.get("address")
        page_url = "https://bruxie.com/"
        id = "".join(j.get("id"))
        street_address = "".join(a.get("street"))
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        location_name = j.get("name")
        country_code = a.get("country")
        store_number = id
        latitude = a.get("lat")
        longitude = a.get("lng")
        location_type = "<MISSING>"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Referer": "https://order.online/store/BruxieOrange-48317/en-US/?hideModal=true&pickup=true",
            "content-type": "application/json",
            "X-Experience-Id": "storefront",
            "X-Channel-Id": "marketplace",
            "apollographql-client-name": "@doordash/app-consumer-production",
            "apollographql-client-version": "0.442.0-production",
            "X-CSRFToken": "",
            "Origin": "https://order.online",
            "Connection": "keep-alive",
            "TE": "Trailers",
        }
        data = (
            '{"operationName":"storepageFeed","variables":{"fulfillmentType":"Pickup","storeId":"'
            + id
            + '","isMerchantPreview":false,"includeNestedOptions":false},"query":"query storepageFeed($storeId: ID!, $menuId: ID, $isMerchantPreview: Boolean, $fulfillmentType: FulfillmentType, $includeNestedOptions: Boolean!) {\\n storepageFeed(storeId: $storeId, menuId: $menuId, isMerchantPreview: $isMerchantPreview, fulfillmentType: $fulfillmentType) {\\n storeHeader {\\n id\\n name\\n description\\n priceRange\\n priceRangeDisplayString\\n offersDelivery\\n offersPickup\\n offersGroupOrder\\n isConvenience\\n isDashpassPartner\\n address {\\n city\\n street\\n displayAddress\\n cityLink\\n __typename\\n }\\n business {\\n id\\n name\\n link\\n differentialPricingEnabled\\n __typename\\n }\\n businessTags {\\n name\\n link\\n __typename\\n }\\n deliveryFeeLayout {\\n title\\n subtitle\\n isSurging\\n displayDeliveryFee\\n __typename\\n }\\n deliveryFeeTooltip {\\n title\\n description\\n __typename\\n }\\n coverImgUrl\\n coverSquareImgUrl\\n businessHeaderImgUrl\\n ratings {\\n numRatings\\n numRatingsDisplayString\\n averageRating\\n isNewlyAdded\\n __typename\\n }\\n distanceFromConsumer {\\n value\\n label\\n __typename\\n }\\n enableSwitchToPickup\\n asapStatus {\\n unavailableStatus\\n displayUnavailableStatus\\n unavailableReason\\n displayUnavailableReason {\\n title\\n subtitle\\n __typename\\n }\\n isAvailable\\n unavailableReasonKeysList\\n __typename\\n }\\n asapPickupStatus {\\n unavailableStatus\\n displayUnavailableStatus\\n unavailableReason\\n displayUnavailableReason {\\n title\\n subtitle\\n __typename\\n }\\n isAvailable\\n unavailableReasonKeysList\\n __typename\\n }\\n status {\\n delivery {\\n isAvailable\\n minutes\\n displayUnavailableStatus\\n unavailableReason\\n isTooFarFromConsumer\\n isStoreInactive\\n __typename\\n }\\n pickup {\\n isAvailable\\n minutes\\n displayUnavailableStatus\\n unavailableReason\\n isStoreInactive\\n __typename\\n }\\n __typename\\n }\\n isMenuV2\\n currency\\n __typename\\n }\\n banners {\\n pickup {\\n id\\n title\\n text\\n __typename\\n }\\n catering {\\n id\\n text\\n __typename\\n }\\n demandGen {\\n id\\n title\\n text\\n modals {\\n type\\n modalKey\\n modalInfo {\\n title\\n description\\n buttonsList {\\n text\\n action\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n demandTest {\\n id\\n title\\n text\\n modals {\\n type\\n modalKey\\n modalInfo {\\n title\\n description\\n buttonsList {\\n text\\n action\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n carousels {\\n id\\n type\\n name\\n description\\n items {\\n id\\n name\\n description\\n displayPrice\\n imgUrl\\n dynamicLabelDisplayString\\n calloutDisplayString\\n nextCursor\\n orderItemId\\n reorderCartId\\n reorderUuid\\n unitAmount\\n currency\\n ... @include(if: $includeNestedOptions) {\\n nestedOptions\\n __typename\\n }\\n specialInstructions\\n __typename\\n }\\n __typename\\n }\\n menuBook {\\n id\\n name\\n displayOpenHours\\n menuCategories {\\n id\\n name\\n numItems\\n next {\\n anchor\\n cursor\\n __typename\\n }\\n __typename\\n }\\n menuList {\\n id\\n name\\n displayOpenHours\\n __typename\\n }\\n __typename\\n }\\n itemLists {\\n id\\n name\\n description\\n items {\\n id\\n name\\n description\\n displayPrice\\n imageUrl\\n dynamicLabelDisplayString\\n calloutDisplayString\\n __typename\\n }\\n __typename\\n }\\n disclaimersList {\\n id\\n text\\n __typename\\n }\\n reviewPreview {\\n maxNumStars\\n consumerReviewData {\\n avgRating\\n numRatings\\n numRatingsDisplayString\\n insufficientRatings\\n consumerReviews {\\n consumerReviewUuid\\n reviewerDisplayName\\n starRating\\n reviewedAt\\n reviewText\\n isVerified\\n experience\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}'
        )
        r = session.post("https://order.online/graphql", headers=headers, data=data)
        js = r.json()["data"]["storepageFeed"]

        hours_of_operation = "<MISSING>"
        openP = js.get("storeHeader").get("status").get("pickup").get("isAvailable")
        if openP:
            hours_of_operation = js.get("menuBook").get("displayOpenHours")
        if not openP:
            hours_of_operation = "Closed"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Referer": "https://order.online/store/bruxie--the-original-fried-chicken-and-waffle-sandwich-48317/en-US",
            "content-type": "application/json",
            "X-Experience-Id": "storefront",
            "X-Channel-Id": "marketplace",
            "apollographql-client-name": "@doordash/app-consumer-production",
            "apollographql-client-version": "0.443.0-production",
            "X-CSRFToken": "",
            "Origin": "https://order.online",
            "Connection": "keep-alive",
            "TE": "Trailers",
        }

        data = (
            '{"operationName":"onlineOrderingStore","variables":{"storeId":"'
            + id
            + '"},"query":"query onlineOrderingStore($storeId: ID!) {\\n onlineOrderingStore(storeId: $storeId) {\\n storeName\\n storePhoneNumber\\n merchantUrl\\n themeEntityId\\n optInRequired\\n themeEntityType\\n logoImage\\n faviconImage\\n phoneNumber\\n privacyPolicyUrl\\n allowedPaymentMethodsForPickupList\\n colors {\\n backgroundHovered\\n toggleBorder\\n backgroundActive\\n backgroundDefault\\n toggleBackground\\n opacity\\n __typename\\n }\\n fonts\\n __typename\\n }\\n}\\n"}'
        )
        r = session.post("https://order.online/graphql", headers=headers, data=data)
        js = r.json()
        phone = js.get("data").get("onlineOrderingStore").get("storePhoneNumber")

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
