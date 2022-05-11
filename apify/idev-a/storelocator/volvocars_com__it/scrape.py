from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("volvocars")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = " http://volvocars.com/it "
urls = {
    "Latvia": "https://www.volvocars.com/lv-lv/dealers/atrodiet-parstavi",
    "New Zealand": "https://www.volvocars.com/nz/dealers/find-a-dealer",
    "Italy": "https://www.volvocars.com/it/dealers/concessionari",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = json.loads(
                bs(session.get(base_url, headers=_headers).text, "lxml")
                .select_one("script#__NEXT_DATA__")
                .text
            )["props"]["pageProps"]["retailers"]
            logger.info(f"[{country}] {len(locations)}")
            for _ in locations:
                street_address = city = state = zip_postal = ""
                s_z = _["addressLine2"].split(",")
                zip_postal = s_z[-1]
                city = s_z[0]
                street_address = _["addressLine1"].replace("\n", " ")

                street_address = street_address.split(zip_postal)[0]

                if country == "Sweden":
                    zip_postal = " ".join(
                        [zz for zz in zip_postal.split() if zz.isdigit()]
                    )

                raw_address = (
                    street_address + " " + city + " " + state + " " + zip_postal
                )

                phone = ""
                if (
                    _["phoneNumbers"]["retailer"]
                    and _["phoneNumbers"]["retailer"] != "0"
                ):
                    phone = _["phoneNumbers"]["retailer"].split("R")[0].strip()
                elif (
                    _["phoneNumbers"]["service"] and _["phoneNumbers"]["service"] != "0"
                ):
                    phone = _["phoneNumbers"]["service"]
                location_type = []
                for lt in _["capabilities"]:
                    if type(lt) == bool:
                        continue
                    location_type.append(lt)
                yield SgRecord(
                    page_url=_["url"] if _["url"] else base_url,
                    location_name=_["name"].split("(")[0],
                    street_address=street_address,
                    city=city.split("(")[0],
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=", ".join(location_type),
                    raw_address=raw_address.replace("\n", ""),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
