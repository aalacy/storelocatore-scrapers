from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hirestation.co.uk"
base_url = "https://brandonhirestation.com/graphql?query=query+getStoreLocations%7BstoreLocations%7Bstore_id+location_id+store_name+address%7Bline_one+line_two+city+county+postcode+phone+email+__typename%7Dcoordinates%7Blat+long+__typename%7Dspecialist+short_description+popular_searches+opening_info+opening_hours%7Bmonday+tuesday+wednesday+thursday+friday+saturday+sunday+__typename%7Durl_key+__typename%7D%7D&operationName=getStoreLocations&variables=%7B%7D"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"][
            "storeLocations"
        ]
        for _ in locations:
            addr = _["address"]
            street_address = ""
            if addr.get("line_one"):
                street_address += " " + addr.get("line_one")
            if addr.get("line_two"):
                street_address += " " + addr.get("line_two")
            ss = street_address.split(",")
            if len(ss) > 1 and ss[-1].strip().endswith("Estate"):
                del ss[-1]
            street_address = (
                ",".join(ss)
                .replace("Georges Industrial Estate", "")
                .replace("Moreton Hall Industrial Estate", "")
                .replace("Barncoose Industrial Estate", "")
                .replace("Chessington Park Industrial Estate", "")
                .replace("Road Industrial Estate", "")
                .replace("Wincheap Industrial Estate", "")
                .strip()
            )
            if street_address.startswith(","):
                street_address = street_address[1:]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            hours = []
            for day, hh in _.get("opening_hours", {}).items():
                if day == "__typename":
                    continue
                hours.append(f"{day}: {hh}")
            page_url = f"https://brandonhirestation.com/branch-finder/{_['url_key']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_["store_name"],
                street_address=street_address,
                city=addr["city"],
                state=addr.get("county"),
                zip_postal=addr["postcode"].split("(")[0],
                latitude=_["coordinates"]["lat"],
                longitude=_["coordinates"]["long"],
                country_code="UK",
                phone=addr["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
