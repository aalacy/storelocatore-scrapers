import csv
from datetime import datetime
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

    locator_domain = "https://www.discounttire.com"
    session = SgRequests()
    data = '{"operationName":"CmsPage","variables":{"id":"/store","siteId":"discounttire"},"query":"query CmsPage($id: String!, $siteId: String) {\\n cms {\\n page(id: $id, siteId: $siteId) {\\n documentTitle\\n metaTags {\\n name\\n content\\n __typename\\n }\\n breadcrumbs {\\n name\\n url\\n __typename\\n }\\n htmlContent\\n source\\n __typename\\n }\\n __typename\\n }\\n}\\n"}'

    r = session.post(
        "https://data.discounttire.com/webapi/discounttire.graph", data=data
    )
    js = r.json()["data"]["cms"]["page"]["htmlContent"]
    tree = html.fromstring(js)
    div = tree.xpath('//a[contains(@href, "store")]')
    s = set()
    for d in div:
        page_url = "https://www.discounttire.com" + "".join(d.xpath(".//@href"))
        slug = "".join(d.xpath(".//@href")).split("/")[-1]
        month = datetime.today().strftime("%b")

        session = SgRequests()
        data = (
            '{"operationName":"StoreByCodeStoreDetailPage","variables":{"storeCode":"'
            + slug
            + '","month":"'
            + month
            + '","sourceLatitude":0,"sourceLongitude":0},"query":"query StoreByCodeStoreDetailPage($storeCode: String!, $month: String!, $dayOfWeek: String, $sourceLatitude: Float, $sourceLongitude: Float) {\\n store {\\n byCode(storeCode: $storeCode, sourceLatitude: $sourceLatitude, sourceLongitude: $sourceLongitude) {\\n address {\\n line1\\n town\\n phone\\n region {\\n isocodeShort\\n __typename\\n }\\n postalCode\\n __typename\\n }\\n baseStore\\n rating {\\n cleanlinessRating\\n knowledgeRating\\n numberOfReviews\\n rating\\n recommendedCount\\n recommendedPercentage\\n __typename\\n }\\n reviewsSummary {\\n rating\\n count\\n __typename\\n }\\n code\\n storeContent\\n distance\\n features {\\n iconName\\n name\\n description\\n code\\n __typename\\n }\\n largeImages: images(format: \\"large\\") {\\n altText\\n url\\n __typename\\n }\\n mediumImages: images(format: \\"medium\\") {\\n altText\\n url\\n __typename\\n }\\n smallImages: images(format: \\"small\\") {\\n altText\\n url\\n __typename\\n }\\n legacyStoreCode\\n geoPoint {\\n latitude\\n longitude\\n __typename\\n }\\n managerName\\n weekDays {\\n holidayType\\n name\\n comment\\n closed\\n closingTime {\\n formattedHour\\n hour\\n minute\\n __typename\\n }\\n formattedDate\\n openingTime {\\n formattedHour\\n hour\\n minute\\n __typename\\n }\\n __typename\\n }\\n popularTimes(month: $month, dayOfWeek: $dayOfWeek) {\\n peakHourData {\\n hourOfDay\\n peakTimesData {\\n avgWaitTime\\n median\\n percentile75\\n mean\\n message\\n stdDev\\n n\\n percentile25\\n __typename\\n }\\n __typename\\n }\\n dayOfWeek\\n __typename\\n }\\n currentTime\\n __typename\\n }\\n __typename\\n }\\n services(storeCode: $storeCode) {\\n name\\n __typename\\n }\\n}\\n"}'
        )
        r = session.post(
            "https://data.discounttire.com/webapi/discounttire.graph", data=data
        )
        js = r.json()
        try:
            a = js.get("data").get("store").get("byCode").get("address")
        except:
            continue

        location_name = "Discount Tire Store"
        location_type = "Store"
        street_address = a.get("line1")
        phone = a.get("phone")
        state = a.get("region").get("isocodeShort")
        postal = a.get("postalCode")
        country_code = "<MISSING>"
        city = a.get("town")
        store_number = slug
        latitude = (
            js.get("data").get("store").get("byCode").get("geoPoint").get("latitude")
        )
        longitude = (
            js.get("data").get("store").get("byCode").get("geoPoint").get("longitude")
        )
        hours = js.get("data").get("store").get("byCode").get("weekDays")
        _tmp = []
        for h in hours:
            date = h.get("formattedDate")
            try:
                t = datetime.strptime(date, "%m/%d/%Y")
            except:
                t = datetime.strptime(date, "%d/%m/%Y")
            day = t.strftime("%A")
            open = h.get("openingTime").get("formattedHour")
            if open is None:
                open = "Closed"
            close = h.get("closingTime").get("formattedHour")
            if close is None:
                close = "Closed"
            line = f"{day} {open} - {close}"
            if open == close:
                line = f"{day} - Closed"
            _tmp.append(line)
        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        line = store_number
        if line in s:
            continue
        s.add(line)

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
