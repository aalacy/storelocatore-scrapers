from bs4 import BeautifulSoup
import csv
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup
from datetime import datetime as dt


logger = SgLogSetup().get_logger("eddiev_com")

session = SgRequests()

headers = {
    "authority": "www.eddiev.com",
    "method": "GET",
    "path": "/locations/all-locations",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": 'AkSession=a697301708760000f60d1760d000000011120200; at_check=true; _confirmations=[%22group%22]; AMCVS_13516EE153222FCE0A490D4D%40AdobeOrg=1; s_cc=true; _fbp=fb.1.1612139900888.1130149707; _gcl_au=1.1.261640792.1612139901; _aeaid=c832eb49-6022-4e9f-94cc-e4588ff80ae7; aeatstartmessage=true; akacd_RWASP-default-phased-release=3789593839~rv=36~id=8c1bc1179a09b08d3cd1e71d3e92029a; DRI_RECENT_LOCATION=5100022; akavpau_dardenvpc=1612303137~id=edbf0100c2072768011bfd93ea609ab8; AKA_A2=A; bm_sz=D117DC3962B47C8A01DD83B50CD5D782~YAAQuJcwFyV2Mbd3AQAAeGrYDguNRGCTudh6+DE5yYW2GSfisic//3H6az2YgkjZxW/03I9+VwjDF2T2EAIH80c1ZhTSSmJFx+jsKpBezMtjI5FCJILVal6+/hc5M7Dsq8tLTwDHizHXc4e5f8uhAURMpoQwWBnEzFFGu1UREwQ7LlmvTwew6Lz0r/ZRjHfn; _abck=F58D1DA52A770F6B5B92AE82F94D2AF5~0~YAAQuJcwF1J2Mbd3AQAAMIHYDgXKYdttBsaxY9mcOxfRAY+TRkXRKN4pbYLMR697MEYn9/AT3KWU5Uahmr11o5jayu/YNF/NoMDlYIpW+ZEHYK6D5JYknrWs9G1NKFsQ9rFx00MIQblWzhARCsU2lX7SY81/EGSKz/I1TdB66fwooiml4EiW1Npkbzh7CSDlYRUUFdtyu9tHzhFJo1c/mhi53eWK8bpOoDNug3Q4yD5cpOREWAmBjtK8ZDZtIz0AyU6QsMsq72ROVrE+M080/79I+BwkkKVNKTcrK7X47XoGDTbAIv1ndGwK4zfOaqDTItToP1dSgR9+o1iUzkwf9NjnWzUl0LYGZHORnTeAD+PQYZoxmdVVwAACHvbmDsEIlPYcIa0=~-1~-1~-1; AMCV_13516EE153222FCE0A490D4D%40AdobeOrg=870038026%7CMCIDTS%7C18694%7CMCMID%7C11120430317841367231681119082570065617%7CMCAAMLH-1615761573%7C7%7CMCAAMB-1615761573%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1615163973s%7CNONE%7CvVersion%7C5.0.0; s_dslv_s=More%20than%2030%20days; s_vnum=1643675899607%26vn%3D5; s_invisit=true; JSESSIONID=gzMO2IS_1smvLKlrTWYPA8Lv6jyBNSwvqA32ojVS2rXFL8g2XRrw!188593891; RT="z=1&dm=eddiev.com&si=7z4jnvmlc6i&ss=klzqn1q1&sl=0&tt=0"; mbox=PC#c5364b6abeb740508f3065d6e9ff0b15.34_0#1678401586|session#2f6c2e5db779497998b6121c9a751cc1#1615158632; s_ppn=ev%7Clocations%20all-locations; s_purl=https%3A%2F%2Fwww.eddiev.com%2Flocations%2Fall-locations; s_nr=1615156786898-Repeat; s_dslv=1615156786899; s_sq=drdardenglobal%3D%2526pid%253Dev%25257Clocations%252520az%252520scottsdale%252520scottsdale%2525208510%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.eddiev.com%25252Flocations%25252Faz%25252Fscottsdale%25252Fscottsdale%25252F8510%252523collapse4%2526ot%253DA; s_ppvl=ev%257Clocations%2520all-locations%2C100%2C86%2C946%2C1536%2C754%2C1536%2C864%2C1.25%2CP; s_ppv=ev%257Clocations%2520all-locations%2C80%2C80%2C754%2C630%2C754%2C1536%2C864%2C1.25%2CL',
    "referer": "https://www.eddiev.com/home",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    url = "https://www.eddiev.com/locations/all-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    storelist = soup.find("div", {"class": "cols"})
    more_link = storelist.findAll("div", {"class", "more_links"})
    for link_div in more_link:
        link = link_div.find("a", {"id": "locDetailsId"})["href"]
        link = "https://www.eddiev.com" + link
        p = session.get(link, headers=headers, verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        left_bar = bs.find("div", {"class": "left-bar"})
        title = left_bar.find("h1", {"class": "style_h1"}).text.strip()
        addr_div = left_bar.find("p")
        addr_div = str(addr_div)
        addr_div = addr_div.strip()
        info = addr_div.split("\n")
        street = info[2]
        street = street.rstrip("<br/>")
        city = info[4]
        city = city.rstrip(",")
        state = info[5].strip()
        pcode = info[6]
        pcode = pcode.rstrip("<br/>")
        phone = info[7]
        phone = phone.rstrip("</p>")
        hours = left_bar.findAll("ul", {"class": "inline top-bar"})
        hrs = ""
        for hr in hours:
            days = hr.findAll("li")
            day = days[0].text.strip()
            time = days[1].text.strip()
            now = dt.today()
            now = now.strftime("%a %b %d")
            time = time.replace(now, "").strip()
            time = time.replace(":00 EST 2021", "").strip()
            hoo = day + " " + time
            hoo = hoo.replace("Today (", "")
            hoo = hoo.replace(")", "").strip()
            hrs = hrs + " " + hoo
        hrs = hrs.strip()
        script = bs.find("script", {"type": "application/ld+json"})
        script = str(script)
        lat = script.split('"latitude":"')[1].split('"')[0]
        lng = script.split('"longitude":"')[1].split('"')[0]
        storeid = link.split("/")[-1]

        data.append(
            [
                "https://www.eddiev.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
                hrs,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
