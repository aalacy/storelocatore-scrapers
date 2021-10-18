from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("furniturerow")

locator_domain = "https://www.furniturerow.com/"
base_url = "https://www.furniturerow.com/v1/location/search/postalcode2"


def fetch_data(http):
    payload = {
        "filter": {
            "postalCode": "57577",
            "country": "USA",
            "term": {
                "cond": {
                    "property": "locationType",
                    "comparator": "eq",
                    "value": "storeCluster",
                }
            },
        },
        "page": 0,
        "pageSize": 500,
        "orders": [],
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "cookie": "guestToken=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3Vwc3RhcnRjb21tZXJjZS5jb20iLCJzdWIiOiJkZW52ZXJtYXR0cmVzczpjdXN0b21lcjo0ZGY1MjNiZi1lZTZhLTQ4MTItOWMzZC0wN2JkMGM5MTc3ZDgiLCJpYXQiOjE2MzI4MjMyNzgsInVzZXJJZCI6IjRkZjUyM2JmLWVlNmEtNDgxMi05YzNkLTA3YmQwYzkxNzdkOCIsImxvZ2luIjoiYW5vbnltb3VzIiwidGVuYW50TWFwIjp7ImRlbnZlcm1hdHRyZXNzIjp7InJvbGVzIjpbImN1c3RvbWVyLmFub255bW91cyJdLCJwZXJtaXNzaW9ucyI6W10sInNpdGVzIjp7IjIwMWNiNzg5LTQxOTgtNDg4Yi1hNWViLTRlN2RmMGZiNGJlZSI6eyJyb2xlcyI6W10sInBlcm1pc3Npb25zIjpbXX0sIjhkM2VhM2JjLWY2NWItNDIyNy05ZmE2LTZmYWU0MGU0NTc1YSI6eyJyb2xlcyI6W10sInBlcm1pc3Npb25zIjpbXX19fX0sInRva2VuVHlwZSI6IkFjY2VzcyIsInRlbmFudCI6ImRlbnZlcm1hdHRyZXNzIiwiZG9tYWluIjoiY3VzdG9tZXIiLCJzdWJqZWN0VHlwZSI6IkFub255bW91cyIsImlzQW5vbnltb3VzIjp0cnVlLCJ0cGUiOiJBQ0NFU1MifQ.5ZiUGEhTqU29thJQNaZ-VoeSuPkGNHChesqh1KxFON0; location=%7B%22postalCode%22%3A%2290045%22%2C%22latitude%22%3A%2233.96%22%2C%22longitude%22%3A%22-118.4%22%7D; store=%7B%22id%22%3A%22100062%22%2C%22name%22%3A%22AZ-Yuma-Furniture%20Row%20Shopping%20Center%22%2C%22address%22%3A%7B%22street1%22%3A%221001%20S.%20Redondo%20Center%20Dr.%22%2C%22street2%22%3A%22%22%2C%22city%22%3A%22Yuma%22%2C%22stateOrRegion%22%3A%22AZ%22%2C%22country%22%3A%22US%22%2C%22postalCode%22%3A%2285365%22%7D%2C%22coordinates%22%3A%7B%22latitude%22%3A32.709191%2C%22longitude%22%3A-114.612422%7D%2C%22locationType%22%3A%22Furniture%20Row%C2%AE%22%2C%22storeId%22%3A%22700354%22%2C%22pricingZone%22%3A%22YUMA%22%2C%22e%22%3A1632909678508%7D; crdlid=%7B%22crdlid%22%3A%223676752002670933%22%7D; _gcl_au=1.1.1794253505.1632823283; dtm_token_sc=AQEDLWF-3M69DQE1DNr_AQEBAQA; _ga=GA1.2.1204994582.1632823285; _gid=GA1.2.327448072.1632823285; _gat_UA-31665-1=1; _uetsid=0a4d8cd0204311ec8b2fa11c74020bf5; _uetvid=0a4e1060204311ec80437d2eccc8d788; dtm_token=AQEDLWF-3M69DQE1DNr_AQEBAQA; _tq_id.TV-09182781-1.5475=9cd3e3ed25b97bc2.1632823285.0.1632823285..; btpdb.YOoTwyE.dGZjLjU0ODM4MzU=U0VTU0lPTg; AMCVS_22602B6956FAB4777F000101%40AdobeOrg=1; AMCV_22602B6956FAB4777F000101%40AdobeOrg=-330454231%7CMCIDTS%7C18899%7CMCMID%7C62176216593391067432292111999276178754%7CMCAAMLH-1633428086%7C9%7CMCAAMB-1633428086%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1632830486s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.1.2; s_cc=true; OptanonAlertBoxClosed=2021-09-28T10:01:34.418Z; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Sep+28+2021+03%3A01%3A34+GMT-0700+(Pacific+Daylight+Time)&version=6.19.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1; s_pers=%20s_vnum%3D1633071600949%2526vn%253D1%7C1633071600949%3B%20gpv_p5%3Dus%257Ceng%257Cfurniturerow_gateway%257Ccon%257Cretailer%257Ccreditoffer%257Ccreditlandingpage%7C1632825096319%3B%20s_nr%3D1632823296324-New%7C1635415296324%3B%20s_invisit%3Dtrue%7C1632825096328%3B%20s_lv%3D1632823296331%7C1727431296331%3B%20s_lv_s%3DFirst%2520Visit%7C1632825096331%3B",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-upstart-tenant": "denvermattress",
    }
    res = http.post(base_url, json=payload, headers=headers)
    store_list = res.json()["items"]
    logger.info(f"{len(store_list)} found")
    for store in store_list:
        page_url = (
            "https://www.furniturerow.com/locations/"
            + store["address"]["city"]
            + "/"
            + store["address"]["stateOrRegion"]
            + "/"
            + store["id"]
        )
        hours_of_operation = store["dynamicProperties"]["stores"][0][
            "dynamicProperties"
        ]["hours"]
        street_address = store["address"]["street1"]
        if store["address"]["street2"]:
            street_address += " " + store["address"]["street2"]

        yield SgRecord(
            page_url=page_url,
            store_number=store["id"],
            location_name=store["name"],
            street_address=street_address,
            city=store["address"]["city"],
            state=store["address"]["stateOrRegion"],
            zip_postal=store["address"]["postalCode"],
            country_code=store["address"]["country"],
            locator_domain=locator_domain,
            latitude=store["coordinates"]["latitude"],
            longitude=store["coordinates"]["longitude"],
            phone=store["contactInformation"]["phoneNumber"],
            hours_of_operation=hours_of_operation,
            location_type=store["locationType"],
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            results = fetch_data(http)
            for rec in results:
                writer.write_row(rec)
