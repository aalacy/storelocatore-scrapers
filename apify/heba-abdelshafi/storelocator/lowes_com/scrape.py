from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.lowes.com/content/lowes/desktop/en_us/stores.xml'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.findAll('loc')
    titlelist = []
    p = 0
    for link in linklist:
        link = link.text
        #print(link)
        r = session.get(link, headers=headers, verify=False)
        try:
            hourlist,r = r.text.split('<script type="application/ld+json">',1)[1].split('</script',1)
            address,r = r.split('<script type="application/ld+json">',1)[1].split('</script',1)
            lat = r.split('"lat":"',1)[1].split('"',1)[0]
            longt = r.split('"long":"',1)[1].split('"',1)[0]
           
            hourlist = json.loads(hourlist)
            address = json.loads(address)        
            street = address['streetAddress']
            city = address['addressLocality']
            state = address['addressRegion']
            pcode = address['postalCode']
            phone = address['telephone']
            title = hourlist['name']
            hourlist = hourlist['openingHours']
            hours = ' '.join(hourlist)
            store = link.split('/')[-1]
            ccode = 'US'
            
           
                    
        except:
            #continue
            headers1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'ocp-apim-subscription-key': 'ee52ddc0d6f3439faf85d704b5787d1d',
            'dtqlws': 'true',
            'cookie': 'AMCV_5E00123F5245B2780A490D45%2540AdobeOrg%40AdobeOrg=1075005958%7CMCMID%7C26942207825055299167297840857947920342%7CMCOPTOUT-1605349460s%7CNONE%7CvVersion%7C4.4.1; ph_aid=039e7dbf-1313-40bd-6c5f-4060482023eb-31e9e62ab5388-4505ec265cdaf-34a239ba743f2; _gcl_au=1.1.113315060.1605342263; __esi__gatekeeper=%7B%22signal%22%3A56%2C%22events%22%3A11%7D; __esi__user=fea863e3-b092-3428-fcbc-6dcedb0f9573; _fbp=fb.1.1605342264770.985724713; _pin_unauth=dWlkPU1XVXhaR1UxWlRNdFlqRTFOUzAwWmprekxUZ3hZamt0TVROa1pEQXhZMkUyTTJZeA; optimizelyEndUserId=oeu1605342265707r0.3435377181428896; LPVID=k2MjI5NzQ3NDNhYjEwMGRi; sf_vis_sts=; _ga=GA1.2.1079705033.1605342268; _scid=a018cbcd-d5e8-47df-8fee-eaa10416aa07; ipe_v=dd089fb4-bf28-21b1-8191-93fcbaa775c9; _sctr=1|1605294000000; SC_ANALYTICS_GLOBAL_COOKIE=590d7188290741ba91c3d5a95c1866a4|True; _minicart=VisitorId=590d7188-2907-41ba-91c3-d5a95c1866a4; ai_user=wX96m|2020-11-14T13:07:19.710Z; sn=2971OL; s_vnum=1606762800206%26vn%3D5; s_getNewRepeat=1605457190627-Repeat; s_daysFromLastVisit=1605457190629; ipe_17331_fov=%7B%22numberOfVisits%22%3A3%2C%22sessionId%22%3A%22fd18d92e-d954-7eb5-1db5-1177ad766e02%22%2C%22expiry%22%3A%222020-12-14T08%3A24%3A30.310Z%22%2C%22lastVisit%22%3A%222020-11-15T16%3A19%3A55.632Z%22%7D; akaalb_ca-prod=~op=CA_GCP_EAST_DFLT:CA_GCP_EAST|~rv=25~m=CA_GCP_EAST:0|~os=842a85c4607824f07d21012037f60849~id=48d734d9dacb602cabec39c8d75119a9; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=1075005958%7CMCIDTS%7C18584%7CMCMID%7C81047891408342885444426177192505527087%7CMCAAMLH-1606203280%7C3%7CMCAAMB-1606203280%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1605605680s%7CNONE%7CvVersion%7C4.4.1; bm_mi=FFB44D182C3D1C1AB49E3963B15BA5C1~r/za2H+YUUX/W8ZSY41bn97wxBsu6CFPyL42LfIQ/8P1fH/SqAcO0BzUfjAAkK/vMYJoq3l3jCN6DuhEC+Gtk3PpGPZRC1p/Ksq7cwf2oEmD+HOxqQtoI6oFZIUrpRgWQhi2imY9/jJD0qnARPiaSGf+MTNvzBD1PMK48LU6mae+LFA5zEM0JIxbR7Y/bPhJsK2XVoSO1gystC9wfDMOodG3doxTKQ4jKpJ4XgGSbcE4f8+GzPYbSAdp7jQdQuUq4mqYW/l2mfSqR8J5STUsV2nXPaD6CWdMGdrDXYbQHmMnezK6a9b5yeA8i8UNULzT; mp_lowes_ca_mixpanel=%7B%22distinct_id%22%3A%20%22175c5daec153c9-06147abf76eb14-230346c-144000-175c5daec1652d%22%2C%22bc_persist_updated%22%3A%201605342260248%7D; ak_bmsc=42A7729D303A66FC4CF3FA8768694E4902109E3D924A0000DC7CB35FBDB37B37~plr5sl8SmujngJj+GIWr1WUsR/s6Y/WqdQaq9Jc9/xrG0gZJvM3mE9TMUZvBTCF9qTezYY1D9JktkeA7IaXGzhItEvCU6NjPyuwkV3UurPuwmtFAC9Z/wNEVjIjl7CO12BJlGktSM/XdbBmJ9MdS5mwHGzFhr+GpM9r+0GVzNSTpy7OZrSOm8UNvDOxHjI6G6qxWsnxtlGHzhCUW8lFpFNIeXzHSuerXBsvnVRF4Qxhvod2y5qTx4obTY0kMkAWl05; __atuvc=9%7C46%2C1%7C47; __atuvs=5fb37d13ded617c6000; _uetsid=5cd5675028a711ebbb76a50e2de776b8; _uetvid=cd5915c0265211eb8676e39c624511a2; _derived_epik=dj0yJnU9cVZQS1U5YzJkQ3YwUjNNbTRRTkZ4NV9SYlJITnQxZlImbj01S2Y2Ml8xRl9uUHEwYThQS2hSaW5nJm09MSZ0PUFBQUFBRi16ZlJZJnJtPTEmcnQ9QUFBQUFGLXpmUlk; LPSID-8130361=RhnLhJ9aSrC6WpcYxw7l1Q; akavpau_default=1605598793~id=44889fbc7c44ffcbc87d2fa9512835ee; bm_sv=245F548D8F4C6916DD1D839B2FB01040~AcoYjzn/Pc46KwYxD3z8ZxEn1mUw9m9jhsJLPIAxRkqHxdgpA50INUuQQ71oMNrDIANNTNJx5fWfgQmYzW+uKQpUaGLmY16RWEU7jWNkdifW+uhiLY4sGSl4Kp96Wf4XN7acoQ8HX+6p+HdwrCVRqQ==; RT="z=1&dm=lowes.ca&si=b8273d92-5648-49f1-b448-082ac2d9fc4c&ss=khlnvo6g&sl=1&tt=0&bcn=%2F%2F684d0d3e.akstat.io%2F&obo=1&ld=97r&r=f6c65eaabd6db55583a693c2f65ad546&ul=97v&hd=9r0"',
            'authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCIsImtpZCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCJ9.eyJhdWQiOiJmZWNkMjQwMC0zZGU4LTRlYmUtYTFmYS1hOTMxMzhhYjA0ZjgiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9mMGY3MDVmZi0zZDNlLTRjMjQtODU0Yy02ZDBiMjBiMmIxMGMvIiwiaWF0IjoxNjA1NTk4MTg0LCJuYmYiOjE2MDU1OTgxODQsImV4cCI6MTYwNTYwMjA4NCwiYWlvIjoiRTJSZ1lCRG45aW5pZXpqRFpXV3czcjZiOS9jWEFRQT0iLCJhcHBpZCI6ImI1Nzk0MjJkLTg5ODEtNGM5NC1iZTU5LTI3MDJlNmQ3N2NlZCIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2YwZjcwNWZmLTNkM2UtNGMyNC04NTRjLTZkMGIyMGIyYjEwYy8iLCJvaWQiOiJjNDlmMGI2YS01OGVkLTRhYzAtYTA5ZC1iOTk3OTYzMDMwYzAiLCJyaCI6IjAuQUFBQV93WDM4RDQ5SkV5RlRHMExJTEt4REMxQ2ViV0JpWlJNdmxrbkF1YlhmTzBTQUFBLiIsInN1YiI6ImM0OWYwYjZhLTU4ZWQtNGFjMC1hMDlkLWI5OTc5NjMwMzBjMCIsInRpZCI6ImYwZjcwNWZmLTNkM2UtNGMyNC04NTRjLTZkMGIyMGIyYjEwYyIsInV0aSI6IkxQX3BvUlc5ZjAyRGI5d21BMFFPQUEiLCJ2ZXIiOiIxLjAifQ.Eq23w8W5GBchKL02GOv15Uu7N1yBPbjzEMgKYbLFeMgaWSgzLUmuQepjjpVyPi6s3SpXYw-RxUKfJssbvn-5k0QN6Ykuu62tMYmz2rX_IRKmZ_lT1fvEOgq9cj2jBRzmUEnEmfKSSxWOE2DiYJXpYzxwixDKMf3yyQqyaqaIUvk0Uxyw_cvdGRa_qJiVI5_vJtdZPBk7ZdtzmcEQ4Uw-6FzhrkR4uyWl79t9-OQMCWpPHeZ33UUFPhq-4j8y7nQV5n9nLVLuj_fXkJCaqpK3Wz0xVTZsFG5xXdp3PKOGQxpRTu6MrDfC6hUdhkzUOgCs6hKXvaMer4gMqYkv7hC-7A'
            
           }
            soup = BeautifulSoup(r.text,'html.parser')
            hours = soup.find('div',{'aria-labelledby':"storeHoursSection"}).text
            r = session.get('https://www.lowes.ca/apim/stores/2922OL', headers=headers1, verify=False).json()
            #print(r)
            pcode = r['zip']
            ccode = 'CA'
            street = r['address']
            state= 'ON'
            city = r['city']
            title = r["store_name"]
            store = r['id']
            phone = r['phone']
        
              
    
        if street in titlelist:
            continue
        titlelist.append(street)
        data.append(['https://www.lowes.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            store,
                            phone,
                            '<MISSING>',
                            lat,
                            longt,
                            hours
                        ])
        
        p += 1
           
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
   

scrape()
