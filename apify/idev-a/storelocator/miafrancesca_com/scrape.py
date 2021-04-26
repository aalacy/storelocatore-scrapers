from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.miafrancesca.com"
        base_url = "https://www.miafrancesca.com/"
        res = session.get(base_url)
        links = bs(res.text, "lxml").select("div#SubMenu-1 ul li a")
        for link in links[1:]:
            page_url = locator_domain + link["href"]
            r1 = session.get(page_url)
            soup = bs(r1.text, "lxml")
            hours = []
            blocks = [
                _
                for _ in soup.select_one("section#intro div.col-md-6").stripped_strings
            ]
            for x, block in enumerate(blocks):
                if block == "HOURS":
                    hours = blocks[x + 1 :]
                    break

            address = " ".join(
                [
                    _
                    for _ in soup.select_one(
                        'a[data-bb-track-category="Address"]'
                    ).stripped_strings
                ]
            )
            addr = parse_address_intl(address)
            phone = soup.select_one('a[data-bb-track-category="Phone Number"]').text

            yield SgRecord(
                page_url=page_url,
                location_name=soup.select_one("h1").text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
