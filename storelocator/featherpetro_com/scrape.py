from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl


locator_domain = "https://www.featherpetro.com"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.featherpetro.com/locations")
        store_links = bs(res.text, "lxml").select(
            "a[data-testid='gallery-item-click-action-link']"
        )
        for store_link in store_links:
            page_url = store_link["href"]
            res = session.get(page_url)
            store = bs(res.text, "lxml")
            address = parse_address_intl(
                store.select(
                    'div[data-testid="mesh-container-content"] div[data-testid="richTextElement"]'
                )[1].text
            )
            location_name = store_link.text
            zip = address.postcode
            state = address.state
            city = address.city
            street_address = address.street_address_1.split("|")[0].strip()
            phone = store.select(
                'div[data-testid="mesh-container-content"] div[data-testid="richTextElement"]'
            )[2].text
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone,
                locator_domain=locator_domain,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
