ffrom lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lacarreta.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Api-Key": "da2-kczsxgnisnd2fgf4ap3hzmabxe",
        "x-amz-user-agent": "aws-amplify/4.3.14 js",
        "Origin": "https://my.atlistmaps.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Referer": "https://my.atlistmaps.com/",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }

    json_data = {
        "query": "mutation CreateEvent($input: CreateEventInput!) {\n  createEvent(input: $input) {\n    id\n    name\n    map {\n      id\n      type\n      name\n      owner\n      createdAt\n      updatedAt\n      defaultZoom\n      gestureHandling\n      zoomHandling\n      zoomControl\n      fullscreenControl\n      streetViewControl\n      scaleControl\n      description\n      descriptionHTML\n      mapType\n      rounding\n      showTraffic\n      showTransit\n      showBicycling\n      showSidebar\n      showModals\n      showDirectionsButton\n      showSearchbox\n      showSidebarAddress\n      showCurrentLocation\n      showTitle\n      showDescription\n      showLightbox\n      showBranding\n      highlightSelectedMarker\n      permission\n      password\n      mapStyle\n      mapStyleGenerated\n      mapStyleRoads\n      mapStyleLandmarks\n      mapStyleLabels\n      mapStyleIcons\n      shapes {\n        nextToken\n      }\n      markers {\n        nextToken\n        scannedCount\n        count\n      }\n      categories {\n        nextToken\n      }\n      events {\n        nextToken\n        scannedCount\n        count\n      }\n      markerColor\n      markerSize\n      markerIcon\n      markerProgrammaticIconType\n      markerShape\n      markerBorder\n      markerBorderColor\n      markerCustomImage\n      markerCustomIcon\n      markerCustomStyle\n      modalWidth\n      modalPosition\n      modalBackgroundColor\n      modalPadding\n      modalRadius\n      modalShadow\n      modalImageHeight\n      modalTail\n      modalTitleVisible\n      modalTitleColor\n      modalTitleSize\n      modalTitleWeight\n      modalAddressVisible\n      modalAddressLink\n      modalAddressColor\n      modalAddressSize\n      modalAddressWeight\n      modalNoteVisible\n      modalNoteColor\n      modalNoteSize\n      modalNoteWeight\n      modalNoteShowFull\n      modalButtonFontColor\n      modalButtonBorderColor\n      modalButtonBackgroundColor\n      modalButtonFontSize\n      modalButtonFullWidth\n      sidebarWidth\n      sidebarBackgroundColor\n      sidebarAccentColor\n      sidebarTitleSize\n      sidebarTitleWeight\n      sidebarDescriptionSize\n      sidebarDescriptionWeight\n      sidebarPosition\n      itemsOrder\n      groupsCollapsed\n      fontPrimary\n      fontSecondary\n      customCSS\n    }\n    createdAt\n    updatedAt\n  }\n}\n",
        "variables": {
            "input": {
                "name": "map viewed",
                "eventMapId": "80977e87-a77f-41f0-8de6-6214785a4e5f",
            },
        },
    }

    r = session.post(
        "https://hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com/graphql",
        headers=headers,
        json=json_data,
    )
    js = r.json()["data"]["createEvent"]["map"]["itemsOrder"]
    for j in js:
        variable_id = j
        page_url = "https://www.lacarreta.com/locations"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Api-Key": "da2-kczsxgnisnd2fgf4ap3hzmabxe",
            "x-amz-user-agent": "aws-amplify/4.3.14 js",
            "Origin": "https://my.atlistmaps.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Referer": "https://my.atlistmaps.com/",
            "Connection": "keep-alive",
        }

        json_data = {
            "query": "query GetMarker($id: ID!) {\n  getMarker(id: $id) {\n    id\n    name\n    lat\n    long\n    placeId\n    formattedAddress\n    notes\n    createdAt\n    updatedAt\n    color\n    icon\n    size\n    shape\n    border\n    borderColor\n    customImage\n    customStyle\n    useCoordinates\n    useHTML\n    imagesOrder\n    map {\n      id\n      name\n      owner\n      createdAt\n      updatedAt\n      markerColor\n      mapStyle\n      defaultZoom\n      zoomControl\n      fullscreenControl\n      streetViewControl\n      scaleControl\n      mapType\n      markers {\n        nextToken\n      }\n    }\n    comments {\n      items {\n        id\n        owner\n        content\n      }\n      nextToken\n    }\n    images(limit: 1000) {\n      items {\n        id\n        name\n        image\n      }\n      nextToken\n    }\n  }\n}\n",
            "variables": {
                "id": f"{variable_id}",
            },
        }

        r = session.post(
            "https://hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com/graphql",
            headers=headers,
            json=json_data,
        )
        js = r.json()["data"]["getMarker"]
        location_name = js.get("name")
        ad = js.get("formattedAddress")
        info = js.get("notes")
        a = html.fromstring(info)
        street_address = str(ad).split(",")[0].strip()
        state = str(ad).split(",")[2].split()[0].strip()
        postal = str(ad).split(",")[2].split()[1].strip()
        country_code = "US"
        city = str(ad).split(",")[1].strip()
        latitude = js.get("lat")
        longitude = js.get("long")
        phone = "".join(a.xpath("./p[1]//text()")) or "<MISSING>"
        hours_of_operation = (
            " ".join(a.xpath("./p[2]//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
