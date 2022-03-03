from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome

session = SgRequests()
headersss = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Cookie": "visid_incap_2413170=iuf6SPzhT+mKcACVBU0bd6U1WGEAAAAAQUIPAAAAAABHeU65cdCOhpFMVpgRMoo9; _gcl_au=1.1.2004528901.1633170860; FPID=FPID2.2.VpN8Vt98sjeWsxZx%2BOAy19RZrM6%2BFwEm4OjFAP7IMEA%3D.1633170861; _st_bid=0939cf00-93d6-11eb-bc89-0f12746e63bb; _fbp=fb.1.1633170870335.967157101; _pin_unauth=dWlkPVpUYzFZbVk1TmprdFlqYzBNQzAwTjJGaUxXSTNaakl0TWpRMU5EZGlORE14WkRWaQ; LPVID=IyNGU3MjQzYzdmOTA4MzYw; _lc2_fpi=7be72f5c8f1d--01fh4116p2fe871kc5t6bxpv70; _ce.s=v11.rlc~1633296622303~v~0185e13a4831b35d27bd29b7f8254eb54ea4e9cd~vpv~0~ir~1; aam_test=aam%3D3684620; aam_uuid_opt=50083103468810933921148224779681165276; nlbi_2413170=WkJ+NqVgmQpV+dKN/cPt3AAAAACBRYLETLbunYtZKsY3dsD7; incap_ses_961_2413170=oGdGVUsdlic/MVGh4ShWDaZewGEAAAAA16jIUOB5dFi/QuJJyR2/Xw==; ASP.NET_SessionId=vw33zkqju2p5r23fxef32k02; _usiTracking=8338335; at_check=true; search_term=; _gid=GA1.2.1235199019.1639997154; AMCV_FA78F19C55BA9FAA7F000101%40AdobeOrg=-1124106680%7CMCIDTS%7C18982%7CMCMID%7C50119964891794107831144045850486083987%7CMCAID%7CNONE%7CMCAAMLH-1640601954%7C3%7CMCAAMB-1640601954%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCOPTOUT-1640004354s%7CNONE%7CvVersion%7C5.2.0; AMCVS_FA78F19C55BA9FAA7F000101%40AdobeOrg=1; gpv_pageName=Facility; s_cc=true; FPLC=3eTjTCM9GSJrS4wOwvy4OevcZUVoLJhhVpEiiun2Dw2zOl8uX78%2Be0zOEzqLc2llMy8x2cZgIySdA2sxdK3ozk3n1iVKHVNnQpvjtMK3irL5by60V459SOXLNhH8qQ%3D%3D; _clck=1yl6h0b|1|exf|0; LPSID-22469663=WOJ4OMsxT3egkNIFFjkmig; _ga=GA1.2.1259643920.1633170861; _derived_epik=dj0yJnU9RWVBYnJ3c0NqNUNKYnliMWZ4cGJVNUV5VGNIRG5PLUImbj1DREtBeTRRM3BGZ0JDTDNWMFEyakhBJm09MSZ0PUFBQUFBR0hBWVAwJnJtPTEmcnQ9QUFBQUFHSEFZUDA; _uetsid=0242f270618211ec9db773564baeeca1; _uetvid=13679d00b01411eb8b98e188bf556b85; mbox=PC#10cd1757245248d0906f34d38600b8c2.38_0#1703242497|session#1ff3a0076d9049868e8f41eb543880b0#1639999557; _clsk=81bxa4|1639997696544|2|1|e.clarity.ms/collect; _ga_M4TC2GYJNB=GS1.1.1639997154.10.1.1639997701.0; s_plt=11.99; s_pltp=Facility; _st=0939cf00-93d6-11eb-bc89-0f12746e63bb.0296e910-6182-11ec-b945-4d8850779b1e.8555664700.(855) 566-4700.+18555664700.0.8772797585.primaryPhone.cshPhone.1639998413.1640008492.600.10800.30.1....0....1...cubesmart^com.UA-1207651-2.1259643920^1633170861.38.",
}


user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")
    with SgChrome(user_agent=user_agent) as driver:
        url = "https://www.cubesmart.com/sitemap-facility.xml"

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll("loc")
        for loc in loclist:

            link = loc.text
            flag = 0

            r = session.get(link, headers=headersss)
            try:
                soup = BeautifulSoup(r.text, "html.parser")
            except:
                driver.get(link)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                flag = 1
            try:
                title = soup.find("h1").text
            except:
                continue
            try:
                address = (
                    soup.find("div", {"class": "csFacilityAddress"}).find("div").text
                )
            except:

                continue
            street, city, state, pcode = address.split(", ")
            if flag == 0:
                lat = r.text.split('"Latitude": ', 1)[1].split(",", 1)[0]
                longt = r.text.split('"Longitude": ', 1)[1].split("}", 1)[0].strip()
                phone = r.text.split('},"telephone":"', 1)[1].split('"', 1)[0]
                try:
                    hours = (
                        r.text.split('<p class="csHoursList">', 1)[1]
                        .split("</p>", 1)[0]
                        .replace("&ndash;", " - ")
                        .replace("<br>", " ")
                        .lstrip()
                    )
                    hours = re.sub(cleanr, " ", hours).strip()
                except:

                    hours = "<MISSING>"
            else:
                lat = driver.page_source.split('"Latitude": ', 1)[1].split(",", 1)[0]
                longt = (
                    driver.page_source.split('"Longitude": ', 1)[1]
                    .split("}", 1)[0]
                    .strip()
                )
                phone = driver.page_source.split('},"telephone":"', 1)[1].split('"', 1)[
                    0
                ]
                try:
                    hours = (
                        driver.page_source.split('<p class="csHoursList">', 1)[1]
                        .split("</p>", 1)[0]
                        .replace("&ndash;", " - ")
                        .replace("<br>", " ")
                        .lstrip()
                    )
                    hours = re.sub(cleanr, " ", hours).strip()
                except:

                    hours = "<MISSING>"
            store = link.split("/")[-1].split(".", 1)[0]

            phone = phone.replace(")", ") ")

            yield SgRecord(
                locator_domain="https://www.cubesmart.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=str(city),
                state=str(state),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=store,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours.replace("<br/>", " ").strip(),
            )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
