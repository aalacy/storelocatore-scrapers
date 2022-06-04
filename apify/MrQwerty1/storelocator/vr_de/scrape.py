from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_urls():
    r = session.get("https://www.vr.de/service/filialen-a-z/a.html", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='module module-linklist ym-clearfix']//a/@href")


def get_params():
    params = dict()
    urls = get_urls()

    for url in urls:
        r = session.get(url, headers=headers)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='module module-teaser ym-clearfix']")

        for d in divs:
            href = "".join(d.xpath(".//a[h2]/@href"))
            name = "".join(d.xpath(".//h2/text()")).strip()
            _id = href.split("-")[-1].replace(".html", "")
            params[_id] = {"name": name, "page_url": href}

    return params


def fetch_data(sgw: SgWriter):
    p = get_params()
    for i in range(1, 100):
        api = f"https://api.geno-datenhub.de/places?_per_page=1000&_page={i}&kind[]=bank&dynamic_attributes.teilnahme_vrde=true&_radius=20000&_fields[]=id&_fields[]=address&_fields[]=contact&_fields[]=kind&_fields[]=subtype&_fields[]=links&_fields[]=name&_fields[]=services&_fields[]=opening_hours&_fields[]=measure_code&_fields[]=is_open&_fields[]=institute&_fields[]=branch_name&_fields[]=uid_vrnet&_fields[]=alternative_bank_name&_fields[]=opening_hours_hint"
        r = session.get(api, headers=headers)
        js = r.json()["data"]
        if not js:
            break

        for j in js:
            a = j.get("address") or {}
            street_address = a.get("street")
            city = a.get("city")
            postal = a.get("zip_code")
            country_code = "DE"
            store_number = j.get("id") or ""
            location_type = j["institute"]["bank_type"]
            _id = store_number.replace("bank-", "").strip()
            page_url = p[_id]["page_url"]
            location_name = p[_id]["name"]
            phone = j["contact"]["i18n_phone_number"]
            latitude = a.get("latitude")
            longitude = a.get("longitude")

            _tmp = []
            hours = j.get("opening_hours") or {}
            for day, inters in hours.items():

                _t = []
                for inter in inters:
                    _t.append(f'{"-".join(inter)}')

                if inters:
                    _tmp.append(f'{day}: {"|".join(_t)}')

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vr.de/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "token": "2MEN71Lg25DxWLysCqC94b2H",
        "Origin": "https://standorte.vr.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Referer": "https://standorte.vr.de/",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
