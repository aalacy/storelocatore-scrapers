import csv
from sgscrape.sgpostal import International_Parser, parse_address
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
    locator_domain = "http://davinails.com"
    api_url = (
        "https://ejlesbezjnd2nbrx55i7kic4om.appsync-api.us-east-1.amazonaws.com/graphql"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Api-Key": "da2-tmt3zkgrzjgybmx5fpgfsd55su",
        "x-amz-user-agent": "aws-amplify/3.8.13 js",
        "Origin": "https://www.atlistmaps.com",
        "Connection": "keep-alive",
        "Referer": "https://www.atlistmaps.com/map/b37b90e4-2e04-4604-acdf-ad47099f14bb?share=true",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    data = '{"query":"query GetMap($id: ID!) {\\n getMap(id: $id) {\\n id\\n name\\n owner\\n markerColor\\n markerShape\\n markerSize\\n markerIcon\\n markerBorder\\n markerCustomImage\\n markerCustomIcon\\n markerCustomStyle\\n defaultZoom\\n gestureHandling\\n zoomHandling\\n zoomControl\\n fullscreenControl\\n streetViewControl\\n mapType\\n showTraffic\\n showTransit\\n showBicycling\\n showSidebar\\n showModals\\n showDirectionsButton\\n showSearchbox\\n showCurrentLocation\\n showTitle\\n showLightbox\\n showBranding\\n highlightSelectedMarker\\n permission\\n password\\n mapStyle\\n mapStyleGenerated\\n mapStyleRoads\\n mapStyleLandmarks\\n mapStyleLabels\\n mapStyleIcons\\n modalPosition\\n modalBackgroundColor\\n modalPadding\\n modalRadius\\n modalShadow\\n modalTail\\n modalTitleVisible\\n modalTitleColor\\n modalTitleSize\\n modalTitleWeight\\n modalAddressVisible\\n modalAddressLink\\n modalAddressColor\\n modalAddressSize\\n modalAddressWeight\\n modalNoteVisible\\n modalNoteColor\\n modalNoteSize\\n modalNoteWeight\\n itemsOrder\\n groupsCollapsed\\n categories(limit: 1000) {\\n items {\\n id\\n name\\n collapsed\\n itemsOrder\\n markerColor\\n markerSize\\n markerIcon\\n markerShape\\n markerBorder\\n markerCustomImage\\n markerCustomIcon\\n }\\n nextToken\\n }\\n shapes(limit: 1000) {\\n items {\\n id\\n lat\\n long\\n zoom\\n name\\n paths\\n fill\\n stroke\\n color\\n width\\n height\\n type\\n }\\n nextToken\\n }\\n markers(limit: 1000) {\\n items {\\n id\\n name\\n lat\\n long\\n placeId\\n formattedAddress\\n notes\\n createdAt\\n color\\n icon\\n size\\n shape\\n border\\n customImage\\n customIcon\\n customStyle\\n useCoordinates\\n }\\n nextToken\\n }\\n }\\n}\\n","variables":{"id":"b37b90e4-2e04-4604-acdf-ad47099f14bb"}}'
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["data"]["getMap"]["markers"]["items"]
    for j in js:
        line = "".join(j.get("formattedAddress"))
        if line.find("DaVi") != -1:
            line = line.split("\n")[1:]
            line = " ".join(line)
        a = parse_address(International_Parser(), line)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city
        postal = a.postcode
        state = a.state
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("name")).split(",")[0]
        phone = j.get("notes")
        phone = str(phone)
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0]
        phone = (
            phone.replace("Phone :", "")
            .replace("<b>Phone:</b>", "")
            .replace("Phone:", "")
            .replace("\n", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("None", "")
            .strip()
        )
        if phone.find("phone & fax") != -1:
            phone = phone.split("phone & fax")[0].strip()
        phone = phone or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "http://davinails.com/locations/"
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
