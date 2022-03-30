import json
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "rh.com"
    start_url = "https://rh.com/rh-experience-layer-v1/graphql"

    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )
    for lat, lng in all_coordinates:
        body = {
            "operationName": "GalleriesByLocation",
            "variables": {"distance": 1000, "lat": str(lat), "lng": str(lng)},
            "query": "query GalleriesByLocation($lat: String!, $lng: String!, $distance: Int! = 1000) {\n  galleriesByLocation(lat: $lat, lng: $lng, distance: $distance) {\n    distance\n    gallery {\n      ...GalleryInfo\n    }\n  }\n}\n\nfragment GalleryInfo on Gallery {\n  __typename\n  docId\n  docType\n  docUuid\n  docCtime\n  docMtime\n  number\n  name\n  type\n  replacementFacility\n  galleryLink\n  address {\n    mallName\n    streetLine1\n    streetLine2\n    city\n    county\n    state\n    country\n    postalCode\n    latitude\n    longitude\n    timeZoneName\n  }\n  phoneNumber\n  url\n  generalEmailAddress\n  leadsEmailAddresses\n  description\n  notes\n  galleryStatus\n  standardDailyHoursList {\n    closeTime\n    dayOfWeek\n    open\n    openTime\n    shortNameEnUs\n  }\n  hours\n  overrideHoursHash {\n    isOpen\n    openTime\n    closeTime\n    shortNameCode\n    shortNameEnUs\n  }\n  collectionOfferings {\n    offersInteriors\n    offersModern\n    offersContemporaryArt\n    offersBabyAndChild\n    offersRugShowroom\n    offersTeen\n    offersOutdoor\n    offersWaterWorks\n  }\n  hospitalityOfferings {\n    offers3ArtsClubCafe\n    offers3ArtsClubWineVault\n    offers3ArtsClubPantryBaristaBar\n    offersRHRooftopRestaurant\n    offersRHCourtyardCafe\n    offersRHWineVault\n    offersRHPantryBaristaBar\n  }\n  groundsFeatures {\n    hasEuropeanGardenCourtyard\n    hasIndoorConservatoryPark\n    hasRooftopParkConservatory\n    hasGroundEstateGardens\n    hasRooftopPark\n    hasGardenCourtyard\n  }\n  serviceOfferings {\n    offersDesignAtelier\n    offersInteriorDesign\n  }\n  parkingOfferings {\n    offersOnStreet\n    offersPrivateFreeLot\n    offersPrivatePaidLot\n    offersPublicFreeLot\n    offersPublicPaidLot\n    offersComplimentaryValet\n    offersPaidValet\n  }\n  region\n  isConciergeEnabled\n  isRHStore\n  isBCStore\n  isRHCAStore\n  isOperating\n  heroImage\n}\n",
        }
        try:
            response = session.post(start_url, json=body, headers=headers)
        except Exception:
            sleep(180)
            continue
        if not response.text:
            continue
        data = json.loads(response.text)
        for poi in data["data"]["galleriesByLocation"]:
            store_url = "https://rh.com/store-locations/{}".format(
                str(poi["gallery"]["number"])
            )
            location_name = poi["gallery"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["gallery"]["address"]["streetLine1"]
            if poi["gallery"]["address"]["streetLine2"]:
                street_address += ", " + poi["gallery"]["address"]["streetLine1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["gallery"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["gallery"]["address"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["gallery"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["gallery"]["address"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["gallery"]["number"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["gallery"]["phoneNumber"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["gallery"]["__typename"]
            latitude = poi["gallery"]["address"]["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["gallery"]["address"]["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = " ".join(poi["gallery"]["hours"])
            hours_of_operation = hours_of_operation.replace("GALLERY", "").split(
                "- - -"
            )[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
