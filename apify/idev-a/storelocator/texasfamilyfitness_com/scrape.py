from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
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
        locator_domain = "https://www.texasfamilyfitness.com/"
        base_url = "https://www.texasfamilyfitness.com/locations"
        r = session.get(base_url, headers=_headers)
        content = bs(r.text, "lxml")
        stores = content.find_all("div", {"class": "location"})

        for store in stores:
            page_url = store.select_one('div[data-hs-cos-field="club_page_link"] a')[
                "href"
            ]
            store_name = store.h2.text
            addr = parse_address_intl(
                " ".join(
                    [
                        " ".join([dd for dd in _.stripped_strings])
                        for _ in store.select("div.address p")
                    ]
                )
            )
            phone = "".join(
                [x for x in store.find("div", {"class": "phone"}).text if x.isnumeric()]
            )
            hours_of_operation = _valid(
                "; ".join(
                    [
                        _.text
                        for _ in store.select('div[data-hs-cos-field="club_hours"] p')
                    ]
                )
            )

            yield SgRecord(
                page_url=page_url,
                location_name=store_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=store["data-location-lat"],
                longitude=store["data-location-lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
