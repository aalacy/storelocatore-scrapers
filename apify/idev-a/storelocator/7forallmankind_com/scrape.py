from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgselenium.sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.7forallmankind.com/"
base_url = "https://www.7forallmankind.com/storelocator/index/ajax/?_=1611046887442"
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(base_url)
        rr = driver.wait_for_request("storelocator/index")
        store_list = json.loads(rr.response.body)
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
                street_address=" ".join(_["address"]).strip(),
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
