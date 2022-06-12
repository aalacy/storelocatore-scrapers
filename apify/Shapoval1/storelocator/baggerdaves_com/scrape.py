import csv
from lxml import html
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

    locator_domain = "https://www.baggerdaves.com/"
    page_url = "https://baggerdaves.com/?page_id=3470"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//section[.//a[text()="ORDER NOW"]]')

    for d in div:

        location_name = "".join(
            d.xpath('.//h3[@class="elementor-image-box-title"]/text()')
        )
        location_type = "Location"
        hours_of_operation = d.xpath('.//p[contains(text(), "Monday")]/text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            "".join(hours_of_operation).replace("\xa0 ", "").replace("pm", "pm ")
        )
        sub_page_url = "".join(d.xpath('.//a[text()="ORDER NOW"]/@href'))

        session = SgRequests()
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        guid = (
            "".join(tree.xpath('//script[contains(text(), "restaurantGuid")]/text()'))
            .split('"restaurantGuid" : "')[1]
            .split('"')[0]
            .strip()
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.toasttab.com/",
            "content-type": "application/json",
            "Toast-Restaurant-External-ID": guid,
            "apollographql-client-name": "takeout-web",
            "apollographql-client-version": "519",
            "toast-customer-access": "",
            "Origin": "https://www.toasttab.com",
            "Connection": "keep-alive",
            "TE": "Trailers",
        }
        data = (
            '[{"operationName":"RESTAURANT_INFO","variables":{"restaurantGuid":"'
            + guid
            + '"},"query":"query RESTAURANT_INFO($restaurantGuid: ID!) {\\n restaurantV2(guid: $restaurantGuid) {\\n ... on Restaurant {\\n guid\\n whiteLabelName\\n description\\n imageUrl\\n bannerUrls {\\n raw\\n __typename\\n }\\n minimumTakeoutTime\\n minimumDeliveryTime\\n location {\\n address1\\n address2\\n city\\n state\\n zip\\n phone\\n latitude\\n longitude\\n __typename\\n }\\n logoUrls {\\n small\\n __typename\\n }\\n schedule {\\n asapAvailableForTakeout\\n todaysHoursForTakeout {\\n startTime\\n endTime\\n __typename\\n }\\n __typename\\n }\\n socialMediaLinks {\\n facebookLink\\n twitterLink\\n instagramLink\\n __typename\\n }\\n giftCardLinks {\\n purchaseLink\\n checkValueLink\\n addValueEnabled\\n __typename\\n }\\n giftCardConfig {\\n redemptionAllowed\\n __typename\\n }\\n specialRequestsConfig {\\n enabled\\n placeholderMessage\\n __typename\\n }\\n spotlightConfig {\\n headerText\\n bodyText\\n __typename\\n }\\n curbsidePickupConfig {\\n enabled\\n enabledV2\\n __typename\\n }\\n popularItemsConfig {\\n enabled\\n __typename\\n }\\n upsellsConfig {\\n enabled\\n __typename\\n }\\n creditCardConfig {\\n amexAccepted\\n tipEnabled\\n __typename\\n }\\n __typename\\n }\\n ... on GeneralError {\\n code\\n message\\n __typename\\n }\\n __typename\\n }\\n}\\n"},{"operationName":"DINING_OPTIONS","variables":{"input":{"restaurantGuid":"'
            + guid
            + '","includeBehaviors":[]}},"query":"query DINING_OPTIONS($input: DiningOptionsInput!) {\\n diningOptions(input: $input) {\\n guid\\n behavior\\n deliveryProvider {\\n provider\\n __typename\\n }\\n asapSchedule {\\n availableNow\\n availableAt\\n __typename\\n }\\n futureSchedule {\\n dates {\\n date\\n timesAndGaps {\\n ... on FutureFulfillmentTime {\\n time\\n __typename\\n }\\n ... on FutureFulfillmentServiceGap {\\n description\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}]'
        )

        session = SgRequests()
        r = session.post(
            "https://ws.toasttab.com/consumer-app-bff/v1/graphql",
            headers=headers,
            data=data,
        )
        js = r.json()[0]["data"]["restaurantV2"]["location"]

        street_address = js.get("address1")
        phone = js.get("phone")
        state = js.get("state")
        postal = js.get("zip")
        city = js.get("city")
        country_code = "US"
        store_number = "<MISSING>"

        latitude = js.get("latitude")
        longitude = js.get("longitude")

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
