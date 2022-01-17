from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thehoneyhole_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://thehoneyhole.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://thehoneyhole.com/"
        r = session.get(url, headers=headers)
        linklist = r.text.split('<div class="order-loc" id=""></p>')[1].split(
            "<p></div>"
        )[0]
        soup = BeautifulSoup(linklist, "html.parser")
        linklist = soup.findAll("a")
        for token in linklist:
            page_url = token["href"]
            log.info(page_url)
            log.info(f"Fetching restaurantGuid from {page_url}")
            r = session.get(page_url, headers=headers)
            token = r.text.split('"restaurantGuid" : "')[1].split('"')[0]
            graphql_url = "https://ws.toasttab.com/consumer-app-bff/v1/graphql"
            payload = (
                '[{"operationName":"RESTAURANT_INFO","variables":{"restaurantGuid":"'
                + token
                + '"},"query":"query RESTAURANT_INFO($restaurantGuid: ID!) {\\n  restaurantV2(guid: $restaurantGuid) {\\n    ... on Restaurant {\\n      guid\\n      whiteLabelName\\n      description\\n      imageUrl\\n      bannerUrls {\\n        raw\\n        __typename\\n      }\\n      minimumTakeoutTime\\n      minimumDeliveryTime\\n      location {\\n        address1\\n        address2\\n        city\\n        state\\n        zip\\n        phone\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      logoUrls {\\n        small\\n        __typename\\n      }\\n      schedule {\\n        asapAvailableForTakeout\\n        todaysHoursForTakeout {\\n          startTime\\n          endTime\\n          __typename\\n        }\\n        __typename\\n      }\\n      socialMediaLinks {\\n        facebookLink\\n        twitterLink\\n        instagramLink\\n        __typename\\n      }\\n      giftCardLinks {\\n        purchaseLink\\n        checkValueLink\\n        addValueEnabled\\n        __typename\\n      }\\n      giftCardConfig {\\n        redemptionAllowed\\n        __typename\\n      }\\n      specialRequestsConfig {\\n        enabled\\n        placeholderMessage\\n        __typename\\n      }\\n      spotlightConfig {\\n        headerText\\n        bodyText\\n        __typename\\n      }\\n      curbsidePickupConfig {\\n        enabled\\n        enabledV2\\n        __typename\\n      }\\n      popularItemsConfig {\\n        enabled\\n        __typename\\n      }\\n      upsellsConfig {\\n        enabled\\n        __typename\\n      }\\n      creditCardConfig {\\n        amexAccepted\\n        tipEnabled\\n        __typename\\n      }\\n      __typename\\n    }\\n    ... on GeneralError {\\n      code\\n      message\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"},{"operationName":"DINING_OPTIONS","variables":{"input":{"restaurantGuid":"bd5b7c06-3501-439e-8338-9a16d558673d","includeBehaviors":[]}},"query":"query DINING_OPTIONS($input: DiningOptionsInput!) {\\n  diningOptions(input: $input) {\\n    guid\\n    behavior\\n    deliveryProvider {\\n      provider\\n      __typename\\n    }\\n    asapSchedule {\\n      availableNow\\n      availableAt\\n      __typename\\n    }\\n    futureSchedule {\\n      dates {\\n        date\\n        timesAndGaps {\\n          ... on FutureFulfillmentTime {\\n            time\\n            __typename\\n          }\\n          ... on FutureFulfillmentServiceGap {\\n            description\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}]'
            )
            headers_1 = {
                "authority": "ws.toasttab.com",
                "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                "apollographql-client-name": "takeout-web",
                "sec-ch-ua-mobile": "?0",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "toast-customer-access": "",
                "content-type": "application/json",
                "accept": "*/*",
                "toast-restaurant-external-id": token,
                "origin": "https://www.toasttab.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.toasttab.com/",
                "accept-language": "en-US,en;q=0.9",
            }
            loclist = session.post(graphql_url, headers=headers_1, data=payload).json()
            for loc in loclist:
                try:
                    loc = loc["data"]["restaurantV2"]
                except:
                    continue
                location_name = loc["whiteLabelName"]
                address = loc["location"]
                try:
                    street_address = address["address1"] + " " + address["address2"]
                except:
                    street_address = address["address1"]
                city = address["city"]
                state = address["state"]
                zip_postal = address["zip"]
                phone = address["phone"]
                latitude = address["latitude"]
                longitude = address["longitude"]
                hours_of_operation = loc["spotlightConfig"]["headerText"]
                hours_of_operation = hours_of_operation.replace("HRS:", "").replace(
                    "Open ", ""
                )
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
