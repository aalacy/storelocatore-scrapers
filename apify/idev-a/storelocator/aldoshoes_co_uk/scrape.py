from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aldoshoes.co.uk"
base_url = "https://aldoshoes.co.uk/apps/store-locator"
detail_url = "https://stores.boldapps.net/front-end/get_store_info.php?shop=aldouk.myshopify.com&data=detailed&store_id={}"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split(
            "markersCoords.push("
        )[1:-2]
        for loc in locations:
            _ = json.loads(loc.split(");")[0])
            raw_address = " ".join(
                bs(
                    _["address"]
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&#039;", "'"),
                    "lxml",
                ).stripped_strings
            )
            info = bs(
                session.get(detail_url.format(_["id"]), headers=_headers).json()[
                    "data"
                ],
                "lxml",
            )
            state = ""
            if info.select_one(".prov_state"):
                state = info.select_one(".prov_state").text.strip()
            hours = []
            if info.select_one(".hours"):
                hours = list(info.select_one(".hours").stripped_strings)[1:]
            yield SgRecord(
                page_url=base_url,
                location_name=info.select_one(".name").text.split("-")[0].strip(),
                street_address=info.select_one(".address").text.strip(),
                city=info.select_one(".city").text.strip(),
                state=state,
                zip_postal=info.select_one(".postal_zip").text.strip(),
                country_code=info.select_one(".country").text.strip(),
                phone=info.select_one(".phone").text.strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
