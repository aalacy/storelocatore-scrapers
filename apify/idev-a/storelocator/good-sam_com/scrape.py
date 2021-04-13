from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("good-sam")

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
    with SgRequests() as session:
        locator_domain = "https://www.good-sam.com/"
        base_url = "https://www.good-sam.com/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        map_data = soup.select('map[name="image-map"] area')
        for _map in map_data:
            url = f"{base_url}#radius=100&address={_map['title']}"
            with SgChrome() as driver:
                driver.get(url)
                for rr in driver.requests:
                    if "coveo/rest/search/v2" in rr.path and rr.response:
                        locations = json.loads(rr.response.body)
                        logger.info(
                            f"[{_map['title']}][{url}]{len(locations['results'])} locations found"
                        )
                        for _ in locations["results"]:
                            logger.info(_["clickUri"])
                            res = session.get(_["clickUri"], headers=_headers)
                            if res.status_code != 200:
                                continue
                            sp1 = bs(res.text, "lxml")
                            sufix = "46747"
                            for key, val in _["raw"].items():
                                if key.startswith("fcity"):
                                    sufix = key.replace("fcity", "")
                            addr = list(
                                sp1.select_one(
                                    "div.location-info__info-col p"
                                ).stripped_strings
                            )
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
                                street_address=addr[0],
                                city=addr[1].split(",")[0].strip(),
                                state=addr[1].split(",")[1].strip(),
                                zip_postal=addr[1].split(",")[2].strip(),
                                country_code="US",
                                latitude=latitude,
                                longitude=longitude,
                                phone=_["raw"][f"fphone{sufix}"],
                                locator_domain=locator_domain,
                            )

                        break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
