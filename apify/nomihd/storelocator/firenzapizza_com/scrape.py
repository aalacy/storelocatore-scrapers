# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "firenzapizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "x-amz-user-agent": "aws-amplify/3.8.13 js",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "x-api-key": "da2-kczsxgnisnd2fgf4ap3hzmabxe",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://www.atlistmaps.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.atlistmaps.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://hin73p6qljbg7aoenfajej2dim.appsync-api.us-east-1.amazonaws.com/graphql"
    )
    data = {
        "query": "query GetMap($id: ID!) {\n  getMap(id: $id) {\n    id\n    name\n    owner\n    markerColor\n    markerShape\n    markerSize\n    markerIcon\n    markerBorder\n    markerCustomImage\n    markerCustomIcon\n    markerCustomStyle\n    defaultZoom\n    gestureHandling\n    zoomHandling\n    zoomControl\n    fullscreenControl\n    streetViewControl\n    mapType\n    showTraffic\n    showTransit\n    showBicycling\n    showSidebar\n    showModals\n    showDirectionsButton\n    showSearchbox\n    showCurrentLocation\n    showTitle\n    showLightbox\n    showBranding\n    highlightSelectedMarker\n    permission\n    password\n    mapStyle\n    mapStyleGenerated\n    mapStyleRoads\n    mapStyleLandmarks\n    mapStyleLabels\n    mapStyleIcons\n    modalPosition\n    modalBackgroundColor\n    modalPadding\n    modalRadius\n    modalShadow\n    modalTail\n    modalTitleVisible\n    modalTitleColor\n    modalTitleSize\n    modalTitleWeight\n    modalAddressVisible\n    modalAddressLink\n    modalAddressColor\n    modalAddressSize\n    modalAddressWeight\n    modalNoteVisible\n    modalNoteColor\n    modalNoteSize\n    modalNoteWeight\n    itemsOrder\n    groupsCollapsed\n    categories(limit: 1000) {\n      items {\n        id\n        name\n        collapsed\n        itemsOrder\n        markerColor\n        markerSize\n        markerIcon\n        markerShape\n        markerBorder\n        markerCustomImage\n        markerCustomIcon\n      }\n      nextToken\n    }\n    shapes(limit: 1000) {\n      items {\n        id\n        lat\n        long\n        zoom\n        name\n        paths\n        fill\n        stroke\n        color\n        width\n        height\n        type\n      }\n      nextToken\n    }\n    markers(limit: 1000) {\n      items {\n        id\n        name\n        lat\n        long\n        placeId\n        formattedAddress\n        notes\n        createdAt\n        color\n        icon\n        size\n        shape\n        border\n        customImage\n        customIcon\n        customStyle\n        useCoordinates\n      }\n      nextToken\n    }\n  }\n}\n",
        "variables": {"id": "5ebd1aee-6da2-4b44-ba46-0cc7624ed52d"},
    }

    stores_req = session.post(search_url, json=data, headers=headers)
    stores = json.loads(stores_req.text)["data"]["getMap"]["markers"]["items"]
    for store in stores:
        page_url = "https://www.firenzapizza.com/location/"

        location_type = "<MISSING>"
        if store["notes"] is not None:
            if "Coming Soon" in store["notes"]:
                location_type = "Coming Soon"

        location_name = store["name"]
        locator_domain = website

        address = store["formattedAddress"].split(",")
        street_address = ", ".join(address[:-3]).strip()
        city = address[-3].strip()
        state_zip = address[-2].strip()
        state = ""
        zip = ""
        if len(state_zip.split(" ")) == 2:
            state = state_zip.split(" ")[0].strip()
            zip = state_zip.split(" ")[-1].strip()
        else:
            state = "<MISSING>"
            zip = state_zip.split(" ")[-1].strip()

        if state == "<MISSING>":
            if "Puerto Rico" in "|".join(address).strip():
                state = "Puerto Rico"

        country_code = "US"

        phone = "<MISSING>"

        hours_of_operation = "<MISSING>"

        store_number = "<MISSING>"

        latitude = store["lat"]
        longitude = store["long"]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
