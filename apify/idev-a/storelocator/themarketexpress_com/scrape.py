from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

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
        locator_domain = "https://www.themarketexpress.com/"
        base_url = "http://www.themarketexpress.com/stores/?view=list"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("#stores li.store")
        for _ in locations:
            if re.search(r"coming soon", _.text, re.IGNORECASE):
                continue
            page_url = _.select_one("a.content")["href"]
            store_number = page_url.split("/")[-2]
            block = [a.text for a in _.select_one("a.content").select("span")]
            state_zip = block[1].split(",")[1].strip()
            yield SgRecord(
                store_number=store_number,
                page_url=page_url,
                location_name=_.a.h2.text,
                street_address=block[0],
                city=block[1].split(",")[0],
                state=state_zip.split(" ")[0],
                zip_postal=state_zip.split(" ")[1],
                country_code="US",
                phone=block[-2],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
