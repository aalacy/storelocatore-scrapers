from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://titanmachinery.com"
base_url = "https://titanmachinery.com/api/default/locations?$orderby=MapName&&$format=application/json;odata.metadata=none&$expand=LocationImage"
country_url = "https://titanmachinery.com/project/vue-scripts?v=C83dTgBrQYohIpDqU1t4B6Teu0n-ookaOf09C1F_gR41"


def fetch_data():
    with SgRequests() as session:
        countries = {}
        for cc in json.loads(
            session.get(country_url, headers=_headers)
            .text.split("countries:")[1]
            .split(",country")[0]
        ):
            countries[cc["code"]] = cc["url"]

        locations = session.get(base_url, headers=_headers).json()["value"]
        for _ in locations:
            addr = _["LocationAddress"]
            days_of_week = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            store_hours = []
            for day in days_of_week:
                week = "LocationSummerHours" + day
                val = _[week] or ""
                if not val:
                    val = "Closed"
                store_hours.append(day + " " + val)
            try:
                page_url = f"https://titanmachinery.com/dealer-locator/{countries[addr.get('CountryCode')]}/{_['UrlName']}"
            except:
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=page_url,
                store_number=_["LocationId"],
                location_name=_["LocationName"],
                street_address=addr["Street"],
                city=addr["City"],
                state=addr.get("StateCode"),
                zip_postal=addr.get("Zip"),
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                country_code=addr.get("CountryCode"),
                phone=_["LocationPhonePrimary"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(store_hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
