from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

base_url = "https://www.robertdyas.co.uk/storefinder"
locator_domain = "https://www.robertdyas.co.uk"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__cfduid=d1cc28f6f77cc7b17fd6d670bec72d6f21612822394; geo-ip-country-code=JP; nostojs=autoload; __cf_bm=abe474d4f5490f8b925c1a84d63134f2834844cf-1612822398-1800-AfDHlHauq84KWhRKe88+10ah27vFdK8Zl2ay0fUcLVONjKRyJvbYnwrAB22itFNi/QblQ7jQhvmIVYsXX/iHjfBbOb79qfEpxdny0WLLvu+3P8/u05brf/gSELdpXkzVj+qhNpC8LhhzMdb3UmdlCNWbYO+gT190bez25bfP7AHh; 2c.cId=6021b77e60b2405a78a536be; BVBRANDID=1fd73a9a-700e-4a64-9c62-6674edffc145; BVBRANDSID=6d0df287-98ac-4e4e-9b78-61435174aa02; form_key=xg4mXQkXA4dEGElS; mage-banners-cache-storage=%7B%7D; PHPSESSID=c110c7ca6dc276db1f76bc18cf0dedd2; _gcl_au=1.1.1055863911.1612822411; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; _ga=GA1.3.1610105765.1612822411; _gid=GA1.3.1793089792.1612822411; _gat_UA-40492181-4=1; _clck=1kweldc; usfu_mGtd8RuUI9RrhF7vSDiyyQ%3d%3d=true; mage-messages=; section_data_ids=%7B%22top-info-bar%22%3A1612822413%7D; recently_viewed_product=%7B%7D; product_data_storage=%7B%7D; recently_compared_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product_previous=%7B%7D; ometria=2_cid%3DIgd4xJkNESFMVyCH%26nses%3D1%26osts%3D1612822400%26sid%3D065e8286yHWa8xUEn7zv%26npv%3D2%26tids%3D%26slt%3D1612822438; _br_uid_2=uid%3D7426753822021%3Av%3D13.0%3Ats%3D1612822413358%3Ahc%3D2; _uetsid=e0d540f06a5a11eb944ecd0d2e0560f2; _uetvid=e0d596606a5a11eb88b80386a06e9c50; _br_uid_2uid=7853181917858:v=13.0:ts=1612779912325:hc=2; OptanonConsent=isIABGlobal=false&datestamp=Mon+Feb+08+2021+17%3A14%3A00+GMT-0500+(Eastern+Standard+Time)&version=6.9.0&landingPath=NotLandingPage&AwaitingReconsent=false&groups=1%3A1%2C2%3A0%2C3%3A0%2C4%3A0%2C0_287186%3A0%2C0_287187%3A0%2C0_287188%3A0%2C0_287189%3A0%2C0_287190%3A0%2C0_287191%3A0%2C0_287192%3A0%2C0_287193%3A0",
    "referer": "https://www.robertdyas.co.uk/",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=headers)
        store_list = json.loads(
            res.text.split('"locations":')[1].split('"template"')[0].strip()[:-1]
        )
        for _ in store_list:
            hours_of_operation = ""
            for x, hh in json.loads(_["schedule_data"]).items():
                hours_of_operation += (
                    x + ": " + hh["open_time"] + " - " + hh["closing_time"] + " "
                )

            yield SgRecord(
                page_url=_["store_url"],
                location_name=_["name"],
                store_number=_["branch_code"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country_id"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation.strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
