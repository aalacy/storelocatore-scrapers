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
        "cookie": "AKA_Lang=en; AKA_POS=US; AKA_Dialect=enUS; visid_incap_1676469=m37dcolQRnCZosWrZ+STscMtaWEAAAAAQUIPAAAAAABFEqml3P+QLcIfjWWfv8Re; incap_ses_7230_1676469=FGCOQ796QiBIWEAr7h5WZM8taWEAAAAAegInzp71Hm2/cp4hBF+bnQ==; AKA_Lang=en; AKA_POS=US; AKA_Dialect=enUS; nlbi_1676469_2232010=wX3URlipumIlJIxsIqPrcgAAAADOqAAiURfdd5vjgc37/6Om; nlbi_1676469_2147483646=c0QIIH6b7kBEnvpYIqPrcgAAAAB/Nf8DYjVMGDXO0gl/D+l4; reese84=3:qGY17dLNhEDXCIY3+CWYIg==:NcJQT6PsAapA5U3dDiuQ6pACLYQpUrYeYvhRWehSVGfqVpBI827UBJ4SoCL4/BenZEV5Oog0ByK0d8Jgg+8MI3Juc7xc2eZvvFHl5yE851ItMrmVhFUafkoaoaUU1vXa33ojwvEj8LbbeEQGNJgtbCpAKod3+OdX7CxwWOkbHlOaUuI+wa/woBqFpNxiTbMBwDOoOoa3pdNJN7LImNuRs/5g2Rspsi5Fnrli+2QEF55fAH9q9cGFV2xPzWDXFOljGZlK9Q9kyX9g0aPb0y+slojmH70D3De8JfcXHqBnRUYGDvofd3hK70u3fJ2STfqYySqbC1foecQRvJ9CGkoQJzDjrXHL18AxJCf3u7/sUAZ/NwdGwNcuhzzaF9XR1veX/OeJC8jE5MRfnhVM7UpVxmIa4+m7LbdfstJGWdso5/PZ4XeKQl/TVnOBNVI4buTP:6zktcGbUuU/sXPKNpzu4L2m2EjUFVlgIG5ZPsjEjTfQ=",
        "if-none-match": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    base_link = "https://www.dollar.com/loc/modules/multilocation/?near_location=US&services__in=&published=1&within_business=true&limit=500"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["objects"]

    locator_domain = "dollar.com"

    for store in stores:
        location_name = store["location_name"]
        try:
            street_address = (store["street"] + " " + store["street2"]).strip()
        except:
            street_address = store["street"].strip()
        if " CLOSE " in street_address.upper():
            continue
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
