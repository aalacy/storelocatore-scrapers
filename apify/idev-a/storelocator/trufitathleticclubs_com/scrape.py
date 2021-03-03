from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

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


def _sign(original, val):
    if "-" in original:
        return f"-{val}"


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://trufitathleticclubs.com/"
        base_url = "https://trufitathleticclubs.com/locations"
        r = session.get(base_url, headers=_headers, verify=False)
        soup = bs(r.text, "html.parser")
        locations = json.loads(
            soup.select_one("locations-select")[":clubs"].replace("&quot;", '"')
        )
        for key, locs in locations.items():
            for loc in locs:
                hours = []
                for key, _ in loc["location_hours"].items():
                    hours.append(f"{key}: {_}")

                url = "-".join(
                    loc["club_name"].replace("Tru Fit", "").strip().split(" ")
                )
                page_url = f"https://trufitathleticclubs.com/clubs?club={url}"
                yield SgRecord(
                    page_url=page_url,
                    store_number=loc["club_id"],
                    location_name=loc["club_name"],
                    street_address=loc["address1"],
                    city=loc["city"],
                    state=loc["state"],
                    zip_postal=loc["zip_code"],
                    country_code="US",
                    location_type=loc["group"],
                    phone=loc["phone"].split("Ext")[0],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid("; ".join(hours)),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
