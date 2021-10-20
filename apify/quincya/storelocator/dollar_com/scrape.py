from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    headers = {
        "authority": "www.dollar.com",
        "method": "GET",
        "path": "/loc/modules/multilocation/?near_location=US&services__in=&published=1&within_business=true&limit=500",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "AKA_Lang=en; AKA_POS=TT; AKA_Dialect=enUS; visid_incap_1676469=m37dcolQRnCZosWrZ+STscMtaWEAAAAAQUIPAAAAAABFEqml3P+QLcIfjWWfv8Re; _gaexp=GAX1.2.YtXyLYzQQ7SkoXcQPoIg8A.18987.1; mbox=session#d0093d7a1abe449aa0c9f19f5b1aa1c4#1634286529|PC#d0093d7a1abe449aa0c9f19f5b1aa1c4.34_0#1697529469; _fbp=fb.1.1634284670840.838865109; _ga=GA1.2.238466776.1634284678; _gcl_au=1.1.885070465.1634284678; C3UID-352=9540274421634284679; C3UID=9540274421634284679; _scid=b5a671de-904c-4987-ba6d-3f486c98ab1c; _uetvid=9dc25dc02d8d11ec80a6837a215af3f3; _sctr=1|1634270400000; nlbi_1676469_2232010=/ix4K4xc1TD6IwQ3IqPrcgAAAABUUZ3TnTheasqwCe6Qpbq9; incap_ses_1430_1676469=nxl6EjXxnRmnv5sGjWHYEx9ubmEAAAAAPqo+yaxinCGEFtmEsDOXwg==; AKA_Lang=en; AKA_POS=TT; AKA_Dialect=enUS; nlbi_1676469_2147483646=7FHgb7HL9mITaYsqIqPrcgAAAAAubtVMAy9VWWot4KP9aKWs; reese84=3:rfz6EYlazBeNnRR2iqdBbQ==:Y2f7vv3sOD+lv10fZVngepm9Xdwbl+L6sBxuVBevwd9bzR0SzDYa5BPJFaMprcqqBXsTubt5uSMwOrtKoKBwtAO/RUUbqFwSlk2vaXZBhwzXGgqly/SmX2yoUEJl8HPRP0sGNj2MXkCcTzl2MfyGEh+VVUpynzPICftl6T2fwjic9hDbqjUfQa/Y+DAJO48GMARNUzHcRNhL5U65LbHIeTlpjLremEEreU8n7cN3KB9LWJUqJP+oJOxtZn82wkgxE3X+NEL5xA++Hzf5su8l+JTn3MFH2yeXN9mC54zqm6YfvjpvZwp585YcCafopKcEmPmHU4OoJkifqPLP8TkZK0fqkTDhS9OQX20/JFtsqtMH5XET177swl+LUSXt9SHldzsux0e3yY73k8gw8e5UwRd8iqAZNbfHevicbguMex/wizqtUJBO17Lz7rPbfWKH:EdcDTKHVN9Ctk5LqbD91B0U1Vp8JhYuJmIFnYCVoMVM=",
        "if-none-match": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    base_link = "https://www.dollar.com/loc/modules/multilocation/?near_location=US&services__in=&published=1&within_business=true&limit=2000"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["objects"]

    locator_domain = "dollar.com"

    found = []
    for store in stores:
        location_name = store["location_name"]
        try:
            street_address = (store["street"] + " " + store["street2"]).strip()
        except:
            street_address = store["street"].strip()

        if " CLOSE " in street_address.upper():
            continue

        if street_address in found:
            continue
        found.append(street_address)

        city = store["city"]
        state = store["state"]
        if not state:
            state = "<MISSING>"
        zip_code = store["postal_code"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        try:
            phone = store["phonemap"]["phone"]
        except:
            phone = "<MISSING>"
        hours_of_operation = ""
        raw_hours = store["formatted_hours"]["primary"]["days"]
        for hour in raw_hours:
            hours_of_operation = (
                hours_of_operation + " " + hour["label"] + " " + hour["content"]
            ).strip()
        latitude = store["lat"]
        longitude = store["lon"]
        link = store["location_url"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
