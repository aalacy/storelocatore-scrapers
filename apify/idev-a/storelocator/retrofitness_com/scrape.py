from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgrequests import SgRequests


def fetch_data():
    locator_domain = "https://retrofitness.com/"
    base_url = "https://retrofitness.com/find-a-gym-near-me/"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "_gcl_au=1.1.2035111968.1609848760; _ga=GA1.2.1658432644.1609848767; _gid=GA1.2.704973794.1609848767; _fbp=fb.1.1609848771090.1480760806; _uetsid=54d463704f4f11eb9b12374fffc48da2; _uetvid=54d471c04f4f11ebb22b310bd104f069; _gat=1",
        "referer": "https://retrofitness.com/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    with SgRequests() as session:
        res = session.get(base_url, headers=headers)
        store_list = json.loads(
            res.text.split('$("#map4").maps(')[1].split(').data("wpgmp_maps")')[0]
        )["places"]
        for store in store_list:
            zip = store["location"]["postal_code"]
            yield SgRecord(
                store_number=store["id"],
                page_url=store["location"]["extra_fields"]["website"],
                location_name=store["title"],
                street_address=store.get("address", "").split(",")[0],
                city=store["location"]["city"],
                state=store["location"]["state"],
                latitude=store["location"]["lat"],
                longitude=store["location"]["lng"],
                zip_postal="0" + zip if len(zip) == 4 else zip,
                country_code=store["location"]["country"],
                phone=store["location"]["extra_fields"]["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
