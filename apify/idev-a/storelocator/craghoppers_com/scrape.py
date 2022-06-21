from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

_headers = {
    "authority": "backend-craghoppers-uk.basecamp-pwa-prod.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "origin": "https://www.craghoppers.com",
    "referer": "https://www.craghoppers.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}

locator_domain = "https://www.craghoppers.com/"
base_url = "https://backend-craghoppers-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1=51.741955750849606&lng1=-0.5444850025390569&lat2=51.31477910442181&lng2=0.34128770253906815"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["result"]["hits"][
            "hits"
        ]
        for loc in locations:
            _ = loc["_source"]
            street_address = _["street"]
            if _["street_line_2"]:
                street_address += ", " + _["street_line_2"]

            hours = []
            hh = json.loads(_["opening_hours"])
            for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                day = day.lower()
                start = ":".join(hh.get(f"{day}_from").split(":")[:-1])
                end = ":".join(hh.get(f"{day}_to").split(":")[:-1])
                hours.append(f"{day}: {start} - {end}")

            raw_address = f"{street_address}, {_['city']}, {_['region']}, {_['postcode']}, {_['country']}"
            raw_address = (
                raw_address.replace(", ,", ",").strip().replace(", GB", "").strip()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            city = _["city"].split(",")[0].strip()
            state = _["region"]
            zip_postal = _["postcode"]

            yield SgRecord(
                page_url="https://www.craghoppers.com/ie/store-locator/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
