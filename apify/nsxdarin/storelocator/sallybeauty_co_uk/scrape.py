from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests(proxy_country="gb")

headers = {
    "authority": "www.sallybeauty.co.uk",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.sallybeauty.co.uk/stores",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "dwac_b3bcb12c80b0372c5fa96f1a58=UdRKiyRcF-nUyhTVDURn2lbfWk0jRbAzvAg%3D|dw-only|||GBP|false|Europe%2FLondon|true; cqcid=ac8v8xpbGMWf9NQggdZlhE9faE; cquid=||; sid=UdRKiyRcF-nUyhTVDURn2lbfWk0jRbAzvAg; dwanonymous_63a37f74b0b171dcfc8aa8d456ae94c2=ac8v8xpbGMWf9NQggdZlhE9faE; _pxhd=JG8yFVmQdVmY1XP8U03XvOD9dNi-qyNYEBPrG5g7rHfklqaTCwp1mJecf-OSPbGK4KCasmCV4OSjUzoLUqPQQA==:rSbmNAa6LmxN/oCnSB1nTLap9ZRI1voKkYVmRdX7E1JYiJ778wpBBtJKcho13yMWIevDjR3FLLltjSGKc50P9e5KVwNfl2GUV20AL5LfFWo=; __cq_dnt=0; dw_dnt=0; dwsid=n-nH-IAZsGB1od5drAL8f5ji1z6HABe6HWOcdum33PizpKL_vlY9o5IEuwPV2QNp_GAUR12u8QQ-DAD5-aACew==; own_hideHeaderTopPromo=true; scarab.visitor=%226978D1ED000A9FA6%22; _ga=GA1.3.1693812091.1631769929; _gid=GA1.3.651631659.1631769929; _fbp=fb.2.1631769929764.1097351228; __cq_uuid=ac8v8xpbGMWf9NQggdZlhE9faE; __cq_seg=0~0.00u00211~0.00u00212~0.00u00213~0.00u00214~0.00u00215~0.00u00216~0.00u00217~0.00u00218~0.00u00219~0.00; pxcts=81e5e2d0-16ae-11ec-894a-699706b06bbf; _pxvid=7f13cca0-16ae-11ec-8718-787450547955; ki_r=; _ce.s=v11.rlc~1631772992536; cto_bundle=j80DHl9BT2hBdVJFa3p1eTV5TjNSTEp3TEVOTEl3VnZPaXRTVVJIOERrNERrNkVZSUZKaFp4dmVSZFQ3RWljbDJweFUzY3c0N2ZNWVNqRkZ6cWpSblFaRGVKVnAxcTNySFdCTTdLNU16VHhQY1dUcCUyQmZ3JTJCeCUyQmJ5VDZLVm5BYlFTQnNpJTJCSkNtTmhJdFBFM0o4NiUyRmR6WUdwdXZRJTNEJTNE; _px3=028d85e71b44d8e6374f629696503c91354509a151a6d7670b0adb83c436cd6c:jYLFqGlRXAHG4FlLtJoaUI66/qVeQo68K6rKSRcf2k4pXtPIKvMvPIBGnk8GtTBC7v7TDsITh0Bif8yuigXYMA==:1000:j6Vz4OPma66srVwsjybJtTePEl5vj+aATXxArHzqxab9H3VT6OMSckA/9pZfJbTvyMe3uTUfGXLC2ZXTvuus9O8VeS6Vjmdjt3YOETuBVLPTaOB5VWZtbc81+R8L8sgCFc/5WkC+U41boaYsf/WyzgWsL+lYuwRvLpV3ulqSGVmDZL3BRcz0ddjpzRsrJaVubqvJlLjvm+7Dn1PsL+Chpw==; ki_t=1631769934245%3B1631769934245%3B1631773022367%3B1%3B3; hideTradePopup=yes; hideCookieBanner=yes; _uetsid=83775f4016ae11eca0b4cfeac0a4d6b0; _uetvid=83777fa016ae11ec9cc101132fc1c484; _gat=1; _pxhd=JG8yFVmQdVmY1XP8U03XvOD9dNi-qyNYEBPrG5g7rHfklqaTCwp1mJecf-OSPbGK4KCasmCV4OSjUzoLUqPQQA==:rSbmNAa6LmxN/oCnSB1nTLap9ZRI1voKkYVmRdX7E1JYiJ778wpBBtJKcho13yMWIevDjR3FLLltjSGKc50P9e5KVwNfl2GUV20AL5LfFWo=; __cq_dnt=0; dw_dnt=0",
}

logger = SgLogSetup().get_logger("sallybeauty_co_uk")


def fetch_data():
    url = "https://www.sallybeauty.co.uk/on/demandware.store/Sites-sally-beauty-Site/en_GB/Stores-GetStoresJSON"
    r = session.get(url, headers=headers).json()
    website = "sallybeauty.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in r:
        store = item["ID"]
        state = "<MISSING>"
        name = item["name"]
        add = item["address"]
        phone = item["phone"]
        city = item["city"]
        zc = item["postalCode"]
        lat = item["latitude"]
        lng = item["longitude"]
        hours = item["hours"]
        loc = "https://www.sallybeauty.co.uk/storeinfo?StoreID=" + store
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if hours == "" or hours is None:
            hours = "<MISSING>"
        addinfo = item["formattedAddress"]
        if addinfo.count(",") == 4:
            add = addinfo.split(",")[0] + " " + addinfo.split(",")[1]
        yield SgRecord(
            locator_domain=website,
            page_url=loc,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
