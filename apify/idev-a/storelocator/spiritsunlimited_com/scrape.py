from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome

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
        locator_domain = "https://spiritsunlimited.com/"
        base_url = "https://spiritsunlimited.com/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        with SgChrome(executable_path=r"/mnt/g/work/mia/chromedriver.exe") as driver:
            script = soup.find("script", id="city-hive-wf-inject-data").string
            locations = driver.execute_script(
                "return " + script.split(" = ")[1].strip()
            )
            for _ in locations["merchant_configs"]:
                _ = _["merchant"]
                page_url = f"https://spiritsunlimited.com/info/?merchant-id={_['id']}"
                hours = []
                for key, hour in _["business_hours"].items():
                    hours.append(f"{key}: {hour['opening']}-{hour['closing']}")
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["address"]["street_address"],
                    city=_["address"]["city"],
                    state=_["address"]["state"],
                    zip_postal=_["address"]["zipcode"],
                    country_code=_["address"]["country_code"],
                    latitude=_["address"]["location"]["coordinates"][0],
                    longitude=_["address"]["location"]["coordinates"][1],
                    location_type=_["type"],
                    phone=_["phone_number"],
                    locator_domain=locator_domain,
                    hours_of_operation=_valid("; ".join(hours)),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
