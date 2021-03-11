from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re

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
        locator_domain = "https://thebuffalospot.com"
        base_url = "https://thebuffalospot.com/our-spots/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.findAll("a", href=re.compile(r"/locations/"))
        for link in links:
            page_url = locator_domain + link["href"]
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            soup = bs(res.text, "lxml")
            _ = json.loads(
                soup.findAll("script", type="application/ld+json")[-1].string.strip()
            )
            yield SgRecord(
                page_url=page_url,
                location_type=_["@type"],
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code=_["address"]["addressCountry"],
                phone=_["telephone"],
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(_["openingHours"]),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
