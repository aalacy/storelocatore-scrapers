from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgFirefox

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    urls = []
    with SgRequests() as session:
        locator_domain = "https://www.good-sam.com/"
        base_url = "https://www.good-sam.com/locations"
        soup = bs(session.get(base_url).text, "lxml")
        map_data = soup.select('map[name="image-map"] area')
        request = ""
        with SgFirefox() as driver:
            for _map in map_data:
                url = f"{base_url}#radius=100&address={_map['title']}"
                driver.get(url)
                for r in driver.requests:
                    if "coveo/rest/v2" in r.path:
                        request = r
                finalUrl = (
                    request.url
                    + "?"
                    + request.body.decode("utf-8").replace(
                        "distance%3C100", "distance%3C1000000"
                    )
                )
                locations = session.get(finalUrl, headers=_headers).json()
                for _ in locations["results"]:
                    if _["clickUri"] in urls:
                        continue
                    urls.append(_["clickUri"])

                    sufix = "46747"
                    if _["raw"].get("faddress46747"):
                        sufix = "46747"
                    if _["raw"].get("faddress79929"):
                        sufix = "79929"
                    if _["raw"].get("fstreetaddress79929"):
                        sufix = "79929"
                    street_address = ""
                    if f"faddress{sufix}" in _["raw"]:
                        street_address = _["raw"][f"faddress{sufix}"]
                    elif f"fstreetaddress{sufix}" in _["raw"]:
                        street_address = _["raw"][f"fstreetaddress{sufix}"]
                    latitude = longitude = ""
                    if f"freflatitude{sufix}" in _["raw"]:
                        latitude = _["raw"][f"freflatitude{sufix}"]
                        longitude = _["raw"][f"freflongitude{sufix}"]
                    elif f"flatitude{sufix}" in _["raw"]:
                        latitude = _["raw"][f"flatitude{sufix}"]
                        longitude = _["raw"][f"flongitude{sufix}"]
                    yield SgRecord(
                        page_url=_["clickUri"],
                        location_name=_["Title"],
                        street_address=street_address,
                        city=_["raw"][f"fcity{sufix}"][0],
                        state=_["raw"][f"fstate{sufix}"][0],
                        country_code="US",
                        latitude=latitude,
                        longitude=longitude,
                        phone=_["raw"][f"fphone{sufix}"],
                        locator_domain=locator_domain,
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
