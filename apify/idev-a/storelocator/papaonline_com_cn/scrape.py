from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.papaonline.com.cn"
base_url = "https://www.papaonline.com.cn/js/chunk-748cb5cd.5da1f691.js"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        cities = json.loads(res.split(",r=")[1].split(",i=")[0])
        locations = json.loads(res.split("d=[],m=")[1].split(",r=[")[0])
        for x, locs in enumerate(locations):
            for _ in locs["restaurant"]:
                addr = parse_address_intl(_["address"])
                ss = _["address"].split("市")
                if len(ss) == 1:
                    street_address = ss[-1]
                else:
                    street_address = "市".join(ss[1:])
                city = addr.city
                if not city or (city and len(city) == 1):
                    city = cities[x]
                if city and len(city) > 3 and "市" in city:
                    city = city.split("市")[0] + "市"
                phone = _.get("phone")
                if phone:
                    phone = phone.replace("暂不外送", "")
                yield SgRecord(
                    page_url="https://www.papaonline.com.cn/#/restaurantList",
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="CN",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=_["time"],
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
