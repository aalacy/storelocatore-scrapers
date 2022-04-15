from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.com.co"
base_url = "https://www.thenorthface.com.co/locales"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locales div.item")
        for _ in locations:
            c_s = _.select_one("div.place").text.strip().split("-")
            info = _.select_one("div.more").text.strip().split("-")
            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one("div.title").text.strip(),
                street_address=_.select_one("div.address").text.strip(),
                city=c_s[0].strip(),
                state=c_s[1].strip(),
                country_code="CO",
                phone=_p(info[1]),
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
