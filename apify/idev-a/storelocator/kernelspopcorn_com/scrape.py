from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Host": "kernels.serveware.io",
    "Origin": "https://www.kernelspopcorn.com",
    "Referer": "https://www.kernelspopcorn.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    if val.endswith(","):
        val = val[:-1]
    return val.strip()


def fetch_data():
    locator_domain = "https://www.kernelspopcorn.com/"
    json_url = "https://kernels.serveware.io/api/bigquery/province/allstores"
    base_url = "https://s3-ap-southeast-1.amazonaws.com/assets-powerstores-com/data/org/13175/theme/22380/js/kernels-stores-locator.js?nocache"
    with SgRequests() as session:
        token = (
            session.get(base_url)
            .text.split("KernelsMap.newToken =")[1]
            .split("//")[0]
            .strip()[1:-2]
        )
        _headers["Authorization"] = f"Bearer {token}"
        locations = session.get(json_url, headers=_headers).json()
        for _ in locations:
            yield SgRecord(
                page_url=_["mall_url"],
                store_number=_["uuid"],
                location_name=_["mall_name"],
                street_address=_valid(_["street"]),
                city=_["city"],
                state=_["province"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
