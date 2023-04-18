from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

locator_domain = "http://www.kfc.hr/"
en_url = "http://www.kfc.hr/en/"
base_url = "https://kfc.hr/en/restaurants"
token_url = "https://api.amrest.eu/amdv/ordering-api/KFC_HR/rest/v1/auth/get-token"
json_url = "https://api.amrest.eu/amdv/ordering-api/KFC_HR/rest/v2/restaurants/"
detail_url = (
    "https://api.amrest.eu/amdv/ordering-api/KFC_HR/rest/v2/restaurants/details/{}"
)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

headers = {
    "content-type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "referer": "https://kfc.hr/",
    "authority": "api.amrest.eu",
}

header1 = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}

header2 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
    "Brand": "KFC",
    "Content-Type": "application/json; charset=UTF-8",
    "Referer": "https://kfc.hr/",
    "sec-ch-ua": '''".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"''',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "Source": "WEB",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}


def fetch_data():
    with SgRequests() as http:
        payload = {
            "deviceUuidSource": "FINGERPRINT",
            "deviceUuid": "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF",
            "source": "WEB_KFC",
        }
        header1["Authorization"] = header2["Authorization"] = (
            "Bearer "
            + http.post(token_url, headers=headers, json=payload).json()["token"]
        )
        locations = http.get(json_url, headers=header1).json()["restaurants"]
        for loc in locations:
            url = detail_url.format(loc["id"])
            logger.info(url)
            _ = http.get(url, headers=header2).json()["details"]

            street_address = _["addressStreet"]
            if _["addressStreetNo"]:
                street_address += " " + _["addressStreetNo"]
            hours = []
            if loc["twentyFourHoursOpen"]:
                hours = ["24 hours"]
            elif _.get("facilityOpenHours"):
                fac = _.get("facilityOpenHours")
                for day in days:
                    _day24 = f"open{day}24h"
                    _day = f"openHours{day}"
                    if fac[_day24]:
                        hours.append(f"{day}: 24 hours")
                    elif fac.get(_day):
                        times = []
                        for hr in fac[_day]:
                            times.append(f"{hr['openFrom']} - {hr['openTo']}")
                        hours.append(f"{day}: {', '.join(times)}")

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["addressCity"],
                zip_postal=_["addressPostalCode"],
                latitude=_["lat"],
                longitude=_["lng"],
                phone=_.get("phoneNo"),
                country_code="Croatia",
                locator_domain=locator_domain,
                hours_of_operation=" ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
