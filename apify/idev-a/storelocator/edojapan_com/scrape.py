from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "Referer": "https://www.edojapan.com/locations/",
    "Host": "www.edojapan.com",
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
        locator_domain = "https://www.edojapan.com"
        base_url = "https://www.edojapan.com/locations/"
        soup = bs(session.get(base_url).text, "lxml")
        links = soup.select("table.location-table tbody tr")
        for link in links:
            page_url = locator_domain + link.a["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _ = json.loads(
                soup1.findAll("script", type="application/ld+json")[-1].string
            )
            latitude = longitude = ""
            if "hasMap" in _:
                coord = _["hasMap"].split("daddr=")[1].split(",")
                latitude = coord[0].strip()
                longitude = coord[-1].strip()
            hours_of_operation = "; ".join(
                [
                    hour
                    for hour in _.get("openingHours", [])
                    if not hour.startswith("HO")
                ]
            )
            if _.get("openingHours", []):
                if _["openingHours"][0] == "Co -":
                    hours_of_operation = "Coming Soon"

            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code=_["address"]["addressCountry"],
                latitude=latitude,
                longitude=longitude,
                phone=_["contactPoint"]["telephone"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
