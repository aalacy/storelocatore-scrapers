from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

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
        locator_domain = "https://www.donelans.com/"
        key_url = "https://api.freshop.com/2/sessions/aa69a2963a0ed813fa0885052c051af7?app_key=donelans"
        token = session.get(key_url, headers=_headers).json()["token"]
        base_url = f"https://api-2.freshop.com/1/stores?app_key=donelans&has_address=true&token={token}"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["items"]:
            yield SgRecord(
                store_number=_["store_number"],
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["address_1"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["phone_md"].split("\n")[0],
                locator_domain=locator_domain,
                hours_of_operation=_valid(_["hours_md"].replace("\n\n", ";")),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
