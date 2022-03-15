from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://northsiderx.com/"


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
        base_url = "https://northsiderx.com/locations"
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        locations = json.loads(
            soup.find("script", type="application/ld+json").string.strip()
        )
        for _ in locations["@graph"]:
            if not _.get("address"):
                continue
            hours = []
            for hour in _["openingHoursSpecification"]:
                time = ""
                day = hour["dayOfWeek"].split("/")[-1]
                if not hour["opens"] and not hour["closes"]:
                    time = "closed"
                else:
                    time = f"{hour['opens']}-{hour['closes']}"
                hours.append(f"{day}: {time}")

            yield SgRecord(
                page_url=base_url,
                location_type=_["@type"],
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code="US",
                phone=_["address"]["telephone"],
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
