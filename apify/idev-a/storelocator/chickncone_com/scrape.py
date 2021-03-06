from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.chickncone.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

_header1 = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "origin": "https://www.chickncone.com",
    "referer": "https://www.chickncone.com/",
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
        locator_domain = "https://www.chickncone.com/"
        base_url = "https://www.chickncone.com/locations-map"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        data_block = json.loads(
            soup.select_one("div.sqs-block.embed-block.sqs-block-embed")[
                "data-block-json"
            ]
        )
        soup1 = bs(data_block["html"], "lxml")
        token = soup1.div["class"][0].split("app-")[1]
        url = f"https://apps.elfsight.com/p/boot/?w={token}"
        locations = session.get(url, headers=_header1).json()
        for _ in locations["data"]["widgets"][token]["data"]["settings"]["markers"]:
            coord = _["coordinates"].split(",")
            if "UAE" in _["position"]:
                continue
            addr = parse_address_intl(_["position"])
            country_code = addr.country or "US"
            hours = []
            if _["infoWorkingHours"]:
                hours = _["infoWorkingHours"].split("|")
            hours_of_operation = "; ".join(hours)
            if "See" in hours_of_operation:
                hours_of_operation = ""
            yield SgRecord(
                page_url=base_url,
                location_name=_["infoTitle"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=_.get("infoPhone"),
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
