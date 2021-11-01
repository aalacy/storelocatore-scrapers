from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgrequests import SgRequests

locator_domain = "https://www.7forallmankind.com/"
base_url = "https://www.7forallmankind.com/storelocator/index/ajax/?_=1611046887442"
_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "cookie": "PHPSESSID=0c51044eabf0940da94e25a619ab3946; visid_incap_2654306=WM72uSRAQo+KogdKrHooIZ65f2EAAAAAQUIPAAAAAAAANbUYQ9OPO9YlM16hIhfZ; incap_ses_882_2654306=4VHjaQ7HyHPVnX7dvn49DJ65f2EAAAAAJ069zwM2TM/RLp1+bald+g==",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(base_url, headers=_headers).json()
        for _ in store_list:
            hours = []
            try:
                hours = json.loads(_["storetime"])
            except:
                tmp = _["storetime"].split('"')[1::2]
                hours = []
                hour = {}
                idx = 0
                while idx < len(tmp):
                    if idx % 14 == 0 and idx > 0:
                        hours.append(hour)
                        hour = {}
                    hour[tmp[idx]] = tmp[idx + 1]
                    idx += 2
                hours.append(hour)
            hours_of_operation = ""
            for hour in hours:
                hours_of_operation += (
                    hour["days"]
                    + ": "
                    + hour["open_hour"]
                    + ":"
                    + hour["open_minute"]
                    + "-"
                    + hour["close_hour"]
                    + ":"
                    + hour["close_minute"]
                    + ""
                )

            yield SgRecord(
                page_url=_["store_url"],
                location_name=_["storename"],
                store_number=_["storelocator_id"],
                street_address=", ".join(_["address"]),
                city=_["city"],
                state=_["region"],
                zip_postal=_["zipcode"],
                country_code=_["country_id"],
                phone=_.get("telephone"),
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
