import time
import random
import tenacity
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt

locator_domain = "https://www.games-workshop.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

api_url = "https://www.games-workshop.com/en-GB/store/fragments/resultsJSON.jsp?latitude=51.5072178&radius=100&longitude=-0.1275862"
cookies = {
    "OptanonConsent": "consentId=003e2a35-f016-4271-8cba-1eaf40fd16a0&datestamp=Fri+Apr+22+2022+13%3A11%3A43+GMT%2B0300+(%D0%92%D0%BE%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B0%D1%8F+%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0%2C+%D0%BB%D0%B5%D1%82%D0%BD%D0%B5%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=6.10.0&interactionCount=2&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=UA%3B53&AwaitingReconsent=false",
    "gw-location": "en_US_gw",
    "__cflb": "02DiuDi8dQVZUWviFxTUssPBRUsSLTELSZudNe2418e1S",
    "ivid": "6a62d84dbb1248b94a0baf7698e35ac562a8d75743",
    "JSESSIONID": "UJhQwU-AgoUPUYetAEpJX0UgINvz4qOJ31e_6HPPwK1ioEI6SMnJWNhE-YPWFds4Llmb3KPLJpdTl2z7KUJt0T7IxQaTxNbS74KegKdCRpeF2hirp4InEGsR_Mn_Gn1l!1885732779",
    "WLS_ROUTE": ".www.d",
    "__cf_bm": "GEGdit85tIGbvu6XdUinR_jlUwcBOZXv3QfEooKFQ54-1650622289-0-Ae8vEJH7NBcKdzf67cBORDqznnA2KwxPAE5wwWYIXhFEzSQ2TSF2ZQi7qVHdQEpBpvIW7ALmZZYvYU2h/3CbHCwnidzNdHrs4Z8s1lXTufnyM1pFVN2A/TQDeCizq8DeV16h3ieNhwsxI0DbMAwWQsawomnAgI1+apue5yzYlpARXFcMnFPfU7iXLGm6hWmEGg==",
    "QueueITAccepted-SDFrts345E-V3_eldritchomensweekend": "EventId%3Deldritchomensweekend%26QueueId%3D00000000-0000-0000-0000-000000000000%26FixedValidityMins%3D3%26RedirectType%3Didle%26IssueTime%3D1650622287%26Hash%3D6eef4020d00894ee6475b7697980cb45da6d3772292e5831ddeaffacc9385b0d",
    "OptanonAlertBoxClosed": "2022-04-22T10:11:34.132Z",
    "_gcl_au": "1.1.1957766227.1650622295",
    "new_user": "true",
    "previous_session": "true",
    "_ga_79M3G6CT1Y": "GS1.1.1650622294.1.1.1650622304.50",
    "_ga": "GA1.2.2044631842.1650622295",
    "_rdt_uuid": "1650622295524.12f81e6d-9da7-4ff4-9eae-1f6e0c2b137f",
    "m_ses": "20220422131135",
    "m_cnt": "1",
    "_gid": "GA1.2.1599692218.1650622297",
    "_fbp": "fb.1.1650622297523.1431529200",
    "_gat_UA-5285490-1": "1",
    "_hjSessionUser_2455086": "eyJpZCI6ImZkZjYwY2NlLTdhZGItNTk1Ny04MDFkLTQ0NTgxYWY5OTdlMiIsImNyZWF0ZWQiOjE2NTA2MjIyOTc1NjMsImV4aXN0aW5nIjp0cnVlfQ==",
    "_hjFirstSeen": "1",
    "_hjIncludedInSessionSample": "1",
    "_hjSession_2455086": "eyJpZCI6ImE5MWUxNzEyLTBiYWQtNDQyOC04MDEwLTdiNzUwZWMwN2E5NiIsImNyZWF0ZWQiOjE2NTA2MjIyOTc2MDIsImluU2FtcGxlIjp0cnVlfQ==",
    "_hjIncludedInPageviewSample": "1",
    "_hjAbsoluteSessionInProgress": "0",
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://www.games-workshop.com/en-US//store/storefinder.jsp",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response():
    with SgRequests() as http:
        response = http.get(api_url, headers=headers, cookies=cookies)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            log.info(f"HTTP STATUS Return: {response.status_code}")
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def fetch_data(sgw: SgWriter):

    r = get_response()
    js = r.json()["locations"]
    for j in js:

        page_url = f'https://www.games-workshop.com/en-US/{j.get("seoUrl")}'
        location_name = j.get("name")
        street_address = j.get("address1")
        postal = j.get("postalCode")
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("telephone")
        store_number = (
            str(j.get("id")).replace("store-gb-", "").replace("UK.C000", "").strip()
        )
        location_type = j.get("type")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
