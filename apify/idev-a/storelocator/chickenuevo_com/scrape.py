from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.chickenuevo.com/"
        base_url = "https://www.chickenuevo.com/locations"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        blocks = [_.text.strip() for _ in soup.select("div#WRchTxt26-13jl p")]
        x = 0
        street_address = city = state = phone = ""
        for block in blocks:
            if not block:
                continue

            if x == 0:
                street_address = block
            if x == 1:
                city = block.split(",")[0]
                state = block.split(",")[1].strip()
            if x == 2:
                phone = block

            x += 1
            if x == 3:
                x = 0
                yield SgRecord(
                    street_address=street_address,
                    city=city,
                    state=state,
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
