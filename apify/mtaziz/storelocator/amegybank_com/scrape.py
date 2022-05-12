from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sglogging import SgLogSetup
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
logger = SgLogSetup().get_logger(logger_name="amegybank_com")
domain = "amegybank.com"
STORE_LOCATOR = "https://www.amegybank.com/branch-locator/"
logger.info(f"Branch Locator: {STORE_LOCATOR}")
api_endpoint_url = "https://www.amegybank.com/locationservices/searchwithfilter"
headers_am_without_cookies = {
    "authority": "www.amegybank.com",
    "method": "POST",
    "path": "/locationservices/searchwithfilter",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "dpr": "1",
    "origin": "https",
    "referer": "https",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "viewport-width": "1851",
    "x-requested-with": "XMLHttpRequest",
}

payload = {
    "channel": "Online",
    "schemaVersion": "1.0",
    "clientUserId": "ZIONPUBLICSITE",
    "clientApplication": "ZIONPUBLICSITE",
    "transactionId": "txId",
    "affiliate": "0175",
    "searchResults": "200",
    "username": "ZIONPUBLICSITE",
    "searchAddress": {
        "address": "10003",
        "city": "",
        "stateProvince": "",
        "postalCode": "",
        "country": "",
    },
    "distance": "3000",
    "searchFilters": [
        {"fieldId": "1", "domainId": "175", "displayOrder": 1, "groupNumber": 1}
    ],
}


def fetch_records():
    with SgRequests() as http:
        rpost = http.post(
            api_endpoint_url,
            data=json.dumps(payload),
            headers=headers_am_without_cookies,
        )
        logger.info(f"HTTPStatusCode: {rpost.status_code}")
        js = rpost.json()
        locs = js["location"]
        logger.info(f"Branch Count: {len(locs)}")
        for idx, _ in enumerate(locs):
            locattr = _["locationAttributes"]
            locname = _["locationName"]
            logger.info(f"[{idx}] [{locname}]")
            loctype = ""
            loctype = [i["value"] for i in locattr if i["name"] == "Other Services"]
            loctype = "".join(loctype)

            hoo = ""
            hoo = "".join(
                [i["value"] for i in locattr if i["name"] == "Location Hours"]
            )

            item = SgRecord(
                locator_domain="amegybank.com",
                page_url="",
                location_name=locname,
                street_address=_["address"],
                city=_["city"],
                state=_["stateProvince"],
                zip_postal=_["postalCode"],
                country_code=_["country"],
                store_number=_["locationId"],
                phone=_["phoneNumber"],
                location_type=loctype,
                latitude=_["lat"],
                longitude=_["long"],
                hours_of_operation=hoo,
                raw_address="",
            )
            yield item


def scrape():
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        for item in fetch_records():
            writer.write_row(item)

    logger.info("Scrape Finished")


if __name__ == "__main__":
    scrape()
