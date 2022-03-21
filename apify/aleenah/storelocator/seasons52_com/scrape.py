from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


headers1 = {
    "authority": "www.seasons52.com",
    "method": "GET",
    "path": "/web-api/reservations/locations",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'email_signup_cookie=2%3Afalse; email_signup_cookie_expire=Sat%2C%2007%20May%202022%2016%3A02%3A38%20GMT; _gcl_au=1.1.868519096.1636128160; _fbp=fb.1.1636128161500.1373840554; __adroll_fpc=d3b6b9ee50d19f85317b57ae56694879-1636128162101; _aeaid=cbc4dc12-d652-44a3-b51f-49cd7e8fad80; AkSession=2f3d6b68475500007b0a8961a80300006a260100; AKA_A2=A; _abck=99DB2B1493C6683990CF448BAA60D9A9~0~YAAQLz1raDz05ex8AQAAIPRQ/wbcCqPOT3CbjAv2kfuxlTH7UDR+wSi68lU88Op5KWxw5RPFDga0RTHOeOE7tnh5ToK+9AHACRRoz1VwcKe7/zmCf4pgfTN7JmP26+Gcw6q24nWmY+fsKKk3zNCFrHIFBfxDB3GOpHbfpXKSCtsVV0md6uIambwqqHY6shXDMsZx/YD+Rxrb7cdzbQzXnoD2Wdcp/8NMvxa8ddkjJsLpkJS0UPn1b/e9PVam7mcJPqtdFpDN2wI+IgFERkgVsv+yYHDcVrtgCiUZJq9Kw3POYIUHCilQt+T3u6I/lhIlGp5lXfYzhT7/LiEcUTwdGIB03swdh6oURYvD4UbeAxGAz2jRdS/N5Btf9hiMwsftpaMFVEm0bSyT1qoYAI3Ux5QYGHnBFNgkHZlI~-1~-1~-1; bm_sz=E90014F0B63A47BC4C4CA619CD9D48AA~YAAQLz1raD705ex8AQAAIPRQ/w0vLmwDYyD9AemHuILAQ8aF9EKzNOLyQUG49g7uulyySplRX1emqsrAwC5DsPeq3zzc2Qm82v2v2MWo31HhENuVt5YeRBC2NFfIAGX6jHRA1gjVCbIyWMFr5ST+QKpttppVOzAdQa1CBQ79MhkctBXS+Ae8RnDiLxbbdk3mdLZB/I2Nninkc9sihWSufzKHAzPWr7IMW1m7hFrLtF0rsmG9rjVrOKTKuKgdshU3uX1RrBNueF7e3wbZfI1GOJMu5l4lJTe1uvghZno652XMS6vRUxU=~4468792~3162434; at_check=true; AMCVS_13516EE153222FCE0A490D4D%40AdobeOrg=1; AMCV_13516EE153222FCE0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C18940%7CMCMID%7C03896145223259375854410228701563857476%7CMCAAMLH-1636975872%7C9%7CMCAAMB-1636975872%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1636378272s%7CNONE%7CvVersion%7C5.2.0; s_dslv_s=Less%20than%207%20days; s_vnum=1667664158351%26vn%3D4; s_invisit=true; s_cc=true; bm_mi=430ADA6C01A768F0DBB011C3F175FAF9~K7wjarjJOV/h7QwOxQUKb7QY05H808k/lDXF+FU2nYJPOLNfsQqn3pACguyPslwub7UXNf0Nyf72MPpnq9+jDeWad5dCL4WeGsa1nPZexCDd7PQNODfYaqj7TE4cycZGSYQfaiJnfYgNwp/k0eFfmYBXxpI3d0ArdrQW8QgmhzY8gxT3VGldbgNvtxFtuzYi9Bgn+5fOhwrEJJoDsFbG2Cc8XhEkMGTXmp/hnXVP20PpVDTKgbW+nHzer/RgEEzk; JSESSIONID=qjD_URvxnI28kk2JDeRcUDwXz0opbeL5CZBmz6zpBynFtc_AUm-u!1419856053; ak_bmsc=54FF82C6A8488075BF7F90289EC01AA7~000000000000000000000000000000~YAAQLz1raKb15ex8AQAAFCFR/w2tz9RsvjYk8zCGVnvDjNtqqkI1Z9xW2h1cthap9NEl2Qw3ASlt4AkqhaTJoVEpgL6Oq7WJNHBDwa6BSwxNoWwlpvtN6n1qXVmLzL2yrW1TuQI40Cr0TwcLft+BLDUY0q3/HqjApL486wXhWRq7f+AOu62SwsVJsJ6NkeHNm2m55hsYBxF+f2eShlmr479TZQZl/NYDeMJpWOSsNuZ7hcsKJtYfazDgA9WHoar3qf2vxdr5h42cpij6vo96tg1vrRxd8ADrIEYuf3nNXnNGhBKfCxI/YyRWU7uZhioJlhv6cEoKYQ217lW0Wi+dRgaQ8xbDS5BhOYsRdq75sLo+JONgOLh+xTNheEe1vtYfA8JAFLxsjZWFAeq8rOftOchqVYVkACKvMnZ8HNaAdWUxPnjGO1isMNe2d9KT94NX+d8tLH3SoaZyZzKlT9aZ4c3JPJlqtKopjfDuhnpwIeCcS+jB8U9OBBK5TsKqd6Q37wWfQH+KIZlK9XbfbYb/D5l9lJQBEMPDV0ParJQ=; aeatstartmessage=true; DRI_RECENT_LOCATION=4600036; DRIREST=4600036@@Birmingham@@33.44941128*-86.72935289@@245 Summit Blvd@@Birmingham@@AL@@35243@@(205) 968-5152@@Sun <span class="times">11:00AM-9:00PM</span> <br>Mon-Thu <span class="times">11:00AM-9:00PM</span> <br>Fri-Sat <span class="times">11:00AM-10:00PM</span> <br>@@true@@~@@4525; DRIRESTAURANTID=4525; s_ppn=s52%7Clocations%20al%20birmingham%20birmingham%204525; s_purl=https%3A%2F%2Fwww.seasons52.com%2Flocations%2Fal%2Fbirmingham%2Fbirmingham%2F4525; s_nr=1636371384247-Repeat; s_dslv=1636371384247; s_sq=%5B%5BB%5D%5D; __ar_v4=DPFQZUONKFBE3GUJIFNSLG%3A20211105%3A12%7CDOUM6LKWIRFWZMI4BQI7LE%3A20211105%3A12; bm_sv=D6581D9575FFDB919674592F781979BA~BYegiB7eR3FzYIa0C2lJdJM7Qr1aD/Ucy87bcY9nJJzdXlio5cRXJ5W4xNiYVUerz+ZoaR1RlKwSCOqLmwnRaTPVXn0i3upzQzpAN06HIah1+f8FVujGsPjZLGf2vDlipxmFKJcClU8I1FBsY3ADzl6xgVKwDg7Hh547FZAMm9E=; RT="z=1&dm=seasons52.com&si=4uiqyjgqbif&ss=kvmkghxi&sl=0&tt=0"; s_ppvl=s52%257Csite-map%2C56%2C56%2C958.7999877929688%2C1536%2C314%2C1536%2C864%2C1.25%2CP; s_ppv=s52%257Clocations%2520al%2520birmingham%2520birmingham%25204525%2C38%2C38%2C754%2C1536%2C754%2C1536%2C864%2C1.25%2CP; mbox=PC#208aef8e4d6146c5bf9f424ae176acec.34_0#1699616190|session#f746cf052e8d4461a5183429eacd10c6#1636373250',
    "referer": "https://www.seasons52.com/locations/al/birmingham/birmingham/4525",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")

    url = "https://www.seasons52.com/locations-sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")
    for link in linklist:
        link = link.text
        store = link.split("/")[-1]
        url = "https://www.seasons52.com/ajax/headerlocation.jsp?restNum=" + str(store)
        headers1["referer"] = link
        loc = (
            session.get(url, headers=headers1).text.replace('"', "").strip().split(",")
        )
        title = loc[1]
        lat, longt = loc[2].split("*", 1)
        street = loc[3]
        city = loc[4]
        state = loc[5]
        pcode = loc[6]
        phone = loc[7]
        hours = re.sub(cleanr, "", loc[8]).strip()
        yield SgRecord(
            locator_domain="https://www.seasons52.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
