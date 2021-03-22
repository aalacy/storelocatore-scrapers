from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("-", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa", "")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.kaiafit.com/"
        base_url = "https://www.kaiafit.com/locations/find-a-kaia-location"
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("locations: ")[1].strip().split("startLat:lat")[0].strip()[:-1]
        )
        for _ in locations:
            yield SgRecord(
                page_url=_["studioLink"],
                store_number=_["studioId"],
                location_name=_["studioName"],
                street_address=f"{_['studioAddress']} {_['studioAddress2']}".strip(),
                city=_["studioCity"],
                state=_["studioState"],
                zip_postal=_["studioZip"],
                country_code=_["studioCountry"],
                phone=_["studioPhone"].replace("(9FIT)", ""),
                latitude=_["studioLat"],
                longitude=_["studioLong"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
