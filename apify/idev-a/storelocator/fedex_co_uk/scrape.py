from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from urllib.parse import urlencode

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fedex.com/"
base_url = "https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores?&callback=jQuery17209410894840796995_1647035934147&projectId=13284125696592996852&where=ST_DISTANCE(geometry%2C+ST_POINT(-0.1275862%2C+51.5072178))%3C160900&version=published&key=AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE&clientId=WDRP&service=list&select=geometry%2C+LOC_ID%2C+PROMOTION_ID%2C+SEQUENCE_ID%2CST_DISTANCE(geometry%2C+ST_POINT(-0.1275862%2C+51.5072178))as+distance&orderBy=distance+ASC&limit=750&maxResults=1000&_=1647035943420"
json_url = "https://6-dot-fedexlocationstaging-1076.appspot.com/rest/search/stores?"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        features = json.loads(
            "{"
            + session.get(base_url, headers=_headers)
            .text.split("jQuery17209410894840796995_1647035934147({")[1]
            .strip()[:-1]
        )["features"]

        where = ""
        for x in range(len(features)):
            loc_id = features[x]["properties"]["LOC_ID"]
            where += f"|LOC_ID='{loc_id}' "
        query = {
            "callback": "jQuery17209410894840796995_1647035934149",
            "projectId": "13284125696592996852",
            "where": where.strip(),
            "version": "published",
            "key": "AIzaSyD5KLv9-3X5egDdfTI24TVzHerD7-IxBiE",
            "clientId": "WDRP",
            "service": where,
            "_": "1648766045990",
        }
        locations = json.loads(
            "{"
            + session.get(json_url + urlencode(query), headers=_headers)
            .text.split("({")[1]
            .strip()[:-1]
        )["features"]
        for loc in locations:
            _ = loc["properties"]
            if _["COMING_SOON_FLAG"] == "1":
                continue
            hours = []
            for day in days:
                day = day.upper()
                open = f"{day}_BUS_HRS_1_OPEN_TIME"
                close = f"{day}_BUS_HRS_1_CLOSE_TIME"
                if _.get(open):
                    hours.append(f"{day}: {_[open]} - {_[close]}")

            street_address = (
                _["ENG_ADDR_LINE_1"]
                .replace("Mail Boxes Etc.", "")
                .replace("Mail Boxes Etc", "")
                .replace("Double Deuce Communications", "")
                .replace("Double Deuce", "")
                .replace("Mail Plus More", "")
                .replace("Postal & Courier Etc", "")
                .replace("The Color Company", "")
                .replace("Prontaprint", "")
                .replace("East Hill Pharmacy", "")
                .replace("Kall Kwik", "")
                .replace("Prontaprint", "")
                .replace("Citibox", "")
                .replace("Stephen Morris Shipping PLC", "")
                .replace("The ShipCentre", "")
                .replace("Snappy Snaps", "")
                .replace("Post and Packing", "")
                .replace("My IPB", "")
                .replace("London Copy Centre", "")
                .replace("Same Day Snaps", "")
                .replace("Gbtel Communications", "")
                .replace("EEL Parcel Point", "")
                .replace("Watney Travel", "")
                .strip()
            )
            if _.get("ENG_ADDR_LINE_2"):
                street_address += " " + _["ENG_ADDR_LINE_2"]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            if street_address.startswith(","):
                street_address = street_address[1:]
            yield SgRecord(
                page_url="https://www.fedex.com/locate/index.html?locale=en_US#",
                store_number=_["LOC_ID"],
                location_name=_["ENG_DISPLAY_NAME"],
                street_address=street_address,
                city=_["ENG_CITY_NAME"],
                zip_postal=f'{_["STATE_CODE"]} {_.get("POSTAL_CODE")}'.strip(),
                latitude=loc["geometry"]["coordinates"][1],
                longitude=loc["geometry"]["coordinates"][0],
                country_code=_["COUNTRY_CODE"],
                phone=_["PHONE_NBR"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
