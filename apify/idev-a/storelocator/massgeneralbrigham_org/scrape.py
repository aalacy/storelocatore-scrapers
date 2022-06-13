from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massgeneralbrigham.org"
base_url = "https://www.massgeneralbrigham.org/find-get-care/find-locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one('script[data-drupal-selector="drupal-settings-json"]')
            .string
        )["geofield_google_map"]["geofield-map-view-locations-attachment-1"]["data"][
            "features"
        ]
        for _ in locations:
            data = _["properties"]["data"]
            addr = bs(data["field_address"], "lxml")
            raw_address = " ".join(addr.stripped_strings)
            street_address = addr.select_one(".address-line1").text.strip()
            if addr.select_one(".address-line2"):
                street_address += " " + addr.select_one(".address-line2").text.strip()
            city = state = zip_postal = ""
            if addr.select_one(".locality"):
                city = addr.select_one(".locality").text.strip()
            if addr.select_one(".administrative-area"):
                state = addr.select_one(".administrative-area").text.strip()
            if addr.select_one(".postal-code"):
                zip_postal = addr.select_one(".postal-code").text.strip()

            page_url = locator_domain + bs(data["title"], "lxml").a["href"]
            name = bs(data["title"], "lxml").text
            location_type = ""
            if "Health Center" in name or ("MGH" in name and "HealthCare" in name):
                location_type = "Community Health Center"
            elif "Vaccine" in name:
                location_type = "COVID-19 Vaccine Center"
            elif "Hospital" in name or "Mass Eye and Ear" in name:
                location_type = "Hospital Care"
            elif (
                "Health Care Center" in name
                or "healthcare" in name.lower()
                or "Community Physicians" in name
                or "Mass General Waltham" in name
            ):
                location_type = "Outpatient Healthcare center"
            elif (
                "Urgent Care" in name
                or "Fast Care" in name
                or "Express Care" in name
                or "ExpressCare" in name
            ):
                location_type = "Urgent Care"
            elif (
                "Outpatient Center" in name
                or "Medical Care" in name
                or "Therapy Center" in name
                or "Outpatient Surgery Center" in name
                or "Spaulding" in name
                or "Outpatient Care" in name
            ):
                location_type = "Rehabilitation"
            yield SgRecord(
                page_url=page_url,
                location_name=name.split("(")[0],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["geometry"]["coordinates"][1],
                longitude=_["geometry"]["coordinates"][0],
                country_code=addr.select_one(".country").text.strip(),
                phone=bs(data["field_phone_number"], "lxml").text.strip(),
                locator_domain=locator_domain,
                location_type=location_type,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
