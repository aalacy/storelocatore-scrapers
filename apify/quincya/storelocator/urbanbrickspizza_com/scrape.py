import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = (
        "https://ejlesbezjnd2nbrx55i7kic4om.appsync-api.us-east-1.amazonaws.com/graphql"
    )

    session = SgRequests()

    headers = {
        "authority": "ejlesbezjnd2nbrx55i7kic4om.appsync-api.us-east-1.amazonaws.com",
        "method": "POST",
        "path": "/graphql",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-amz-user-agent": "aws-amplify/3.8.15 js",
        "x-api-key": "da2-tmt3zkgrzjgybmx5fpgfsd55su",
    }

    json = {
        "query": "query GetMap($id: ID!) {\n  getMap(id: $id) {\n    id\n    name\n    owner\n    markerColor\n    markerShape\n    markerSize\n    markerIcon\n    markerProgrammaticIconType\n    markerBorder\n    markerCustomImage\n    markerCustomIcon\n    markerCustomStyle\n    defaultZoom\n    gestureHandling\n    zoomHandling\n    zoomControl\n    fullscreenControl\n    streetViewControl\n    mapType\n    showTraffic\n    showTransit\n    showBicycling\n    showSidebar\n    showModals\n    showDirectionsButton\n    showSearchbox\n    showCurrentLocation\n    showTitle\n    showLightbox\n    showBranding\n    highlightSelectedMarker\n    permission\n    password\n    mapStyle\n    mapStyleGenerated\n    mapStyleRoads\n    mapStyleLandmarks\n    mapStyleLabels\n    mapStyleIcons\n    modalPosition\n    modalBackgroundColor\n    modalPadding\n    modalRadius\n    modalShadow\n    modalTail\n    modalTitleVisible\n    modalTitleColor\n    modalTitleSize\n    modalTitleWeight\n    modalAddressVisible\n    modalAddressLink\n    modalAddressColor\n    modalAddressSize\n    modalAddressWeight\n    modalNoteVisible\n    modalNoteColor\n    modalNoteSize\n    modalNoteWeight\n    itemsOrder\n    groupsCollapsed\n    categories(limit: 1000) {\n      items {\n        id\n        name\n        collapsed\n        itemsOrder\n        markerColor\n        markerSize\n        markerIcon\n        markerProgrammaticIconType\n        markerShape\n        markerBorder\n        markerCustomImage\n        markerCustomIcon\n      }\n      nextToken\n    }\n    shapes(limit: 1000) {\n      items {\n        id\n        lat\n        long\n        zoom\n        name\n        paths\n        fill\n        stroke\n        color\n        width\n        height\n        type\n      }\n      nextToken\n    }\n    markers(limit: 1000) {\n      items {\n        id\n        name\n        lat\n        long\n        placeId\n        formattedAddress\n        notes\n        createdAt\n        color\n        icon\n        size\n        shape\n        border\n        customImage\n        customIcon\n        customStyle\n        useCoordinates\n        images(limit: 1000) {\n          items {\n            id\n            name\n            image\n          }\n          nextToken\n        }\n      }\n      nextToken\n    }\n  }\n}\n",
        "variables": {"id": "5ebd1aee-6da2-4b44-ba46-0cc7624ed52d"},
    }

    stores = session.post(base_link, headers=headers, json=json).json()["data"][
        "getMap"
    ]["markers"]["items"]

    data = []
    locator_domain = "urbanbrickskitchen.com"

    for store in stores:
        location_name = store["name"]
        raw_address = store["formattedAddress"].split(",")
        street_address = " ".join(raw_address[:-3]).replace("  ", " ").strip()
        city = raw_address[-3].strip()
        state = raw_address[-2].split()[0].strip()
        if state.isdigit():
            zip_code = state
            state = "<MISSING>"
        else:
            zip_code = raw_address[-2].split()[1].strip()
        country_code = raw_address[-1].strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        latitude = store["lat"]
        longitude = store["long"]
        link = "https://urbanbrickskitchen.com/locations/"
        hours_of_operation = "<MISSING>"

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
