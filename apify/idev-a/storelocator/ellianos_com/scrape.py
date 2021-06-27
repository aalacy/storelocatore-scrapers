from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.ellianos.com/"
    base_url = "https://www.ellianos.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=9fe95f4d86&load_all=1&layout=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if "COMING SOON" in _["title"]:
                continue
            hours = []
            is_coming_soon = False
            for day, hh in json.loads(_["open_hours"]).items():
                times = hh[0]
                if hh[0] == "0":
                    if day == "mon":
                        is_coming_soon = True
                        break
                    else:
                        times = "closed"
                hours.append(f"{day}: {times}")
            if is_coming_soon:
                continue
            yield SgRecord(
                page_url=_["website"],
                location_name=_["title"],
                store_number=_["id"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
