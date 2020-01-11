import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    canada = ['Toronto,ON','Montreal,QB','Calgary,AB','Ottawa,ON','Edmonton,AB','Mississauga,ON','Winnipeg,MB','Vancouver,BC','Brampton,ON','Hamilton,ON','Quebec,QB','Surrey,BC','Laval,QB','Halifax,NS','London,ON','Markham,ON','Vaughan,ON','Gatineau,QB','Saskatoon,SK','Longueuil,QB','Kitchener,ON','Burnaby,BC','Windsor,ON','Regina,SK','Richmond,BC','Richmond Hill,ON','Oakville,ON','Burlington,ON','Greater Sudbury,ON','Sherbrooke,QB','Oshawa,ON','Saguenay,QB','Levis,QB','Barrie,ON','Abbotsford,BC','Coquitlam,BC','Trois Rivieres,QB','St Catharines,ON','Guelph,ON','Cambridge,ON','Whitby,ON','Kelowna,BC','Kingston,ON','Ajax,ON','Langley District Municipality,BC','Saanich,BC','Terrebonne,QB','Milton,ON','St Johns,NL','Thunder Bay,ON','Waterloo,ON','Delta,BC','Chatham Kent,ON','Red Deer,AB','Strathcona County,AB','Brantford,ON','St Jean sur Richelieu,QB','Cape Breton,NS','Lethbridge,AB','Clarington,ON','Pickering,ON','Nanaimo,BC','Kamloops,BC','Niagara Falls,ON','North Vancouver District Municipality,BC','Victoria,BC','Brossard,QB','Repentigny,QB','Newmarket,ON','Chilliwack,BC','Maple Ridge,BC','Peterborough,ON','Kawartha Lakes,ON','Drummondville,QB','St Jerome,QB','Prince George,BC','Sault Ste Marie,ON','Moncton,NB','Sarnia,ON','Wood Buffalo,AB','New Westminster,BC','St John,NB','Caledon,ON','Granby,QB','St Albert,AB','Norfolk County,ON','Medicine Hat,AB','Grande Prairie,AB','Airdrie,AB','Halton Hills,ON','Port Coquitlam,BC','Fredericton,NB','Blainville,QB','St Hyacinthe,QB','Aurora,ON','North Vancouver,BC','Welland,ON','North Bay,ON','Belleville,ON','Mirabel,QB','Shawinigan,QB','Dollard Des Ormeaux,QB','Brandon,MB','Rimouski,QB','Chateauguay,QB','Mascouche,QB','Cornwall,ON','Victoriaville,QB','Whitchurch Stouffville,ON','Haldimand County,ON','Georgina,ON','St Eustache,QB','Quinte West,ON','West Vancouver,BC','Rouyn Noranda,QB','Timmins,ON','Boucherville,QB','Woodstock,ON','Salaberry de Valleyfield,QB','Vernon,BC','St Thomas,ON','Mission,BC','Vaudreuil Dorion,QB','Brant,ON','Lakeshore,ON','Innisfil,ON','Charlottetown,PE','Prince Albert,SK','Langford,BC','Bradford West Gwillimbury,ON','Sorel Tracy,QB','New Tecumseth,ON','Spruce Grove,AB','Moose Jaw,SK','Penticton,BC','Port Moody,BC','West Kelowna,BC','Campbell River,BC','St Georges,QB','Val dOr,QB','Cote St Luc,QB','Stratford,ON','Pointe Claire,QB','Orillia,ON','Alma,QB','Fort Erie,ON','LaSalle,ON','Leduc,AB','Ste Julie,QB','North Cowichan,BC','Chambly,QB','Orangeville,ON','Okotoks,AB','Leamington,ON','St Constant,QB','Grimsby,ON','Boisbriand,QB','Magog,QB','St Bruno de Montarville,QB','Conception Bay South,NL','Ste Therese,QB','Langley,BC','Cochrane,AB','Courtenay,BC','Thetford Mines,QB','Sept Iles,QB','Dieppe,NB','Whitehorse,YT','Prince Edward County,ON','Clarence Rockland,ON','Fort Saskatchewan,AB','La Prairie,QB','East Gwillimbury,ON','Lincoln,ON','Tecumseh,ON','Mount Pearl,NL','Beloeil,QB','LAssomption,QB','Amherstburg,ON','St Lambert,QB','Collingwood,ON','Kingsville,ON','Baie Comeau,QB','Paradise,NL','Brockville,ON','Owen Sound,ON','Varennes,QB','Candiac,QB','Strathroy Caradoc,ON','St Lin Laurentides,QB','Wasaga Beach,ON','Joliette,QB','Essex,ON','Westmount,QB','Mont Royal,QB','Fort St John,BC','Kirkland,QB','Cranbrook,BC','White Rock,BC','St Lazare,QB']
    for loc in canada:
        print('Pulling City %s...' % loc)
        ccity = loc.split(',')[0].strip()
        cprov = loc.split(',')[1].strip()
        url = 'https://www.ford.ca/services/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&city=' + ccity + '&province=' + cprov
        r = session.get(url, headers=headers)
        if '"Dealer":[{' in r.content:
            for item in json.loads(r.content)['Response']['Dealer']:
                lng = item['Longitude']
                lat = item['Latitude']
                name = item['Name']
                typ = item['dealerType']
                website = 'ford.ca'
                purl = item['URL']
                hours = ''
                add = item['Address']['Street1'] + ' ' + item['Address']['Street2'] + ' ' + item['Address']['Street3']
                add = add.strip()
                city = item['Address']['City']
                state = item['Address']['Province']
                country = item['Address']['Country'][:2]
                zc = item['Address']['PostalCode']
                store = item['SalesCode']
                phone = item['Phone']
                daytext = str(item['SalesHours'])
                daytext = daytext.replace("'",'"')
                daytext = daytext.replace('u"','"').replace(' {','{')
                days = daytext.split(',{')
                for day in days:
                    if '"name": "' in day:
                        dname = day.split('"name": "')[1].split('"')[0]
                        if '"closed": "true"' in day:
                            hrs = 'Closed'
                        else:
                            hrs = day.split('"open": "')[1].split('"')[0] + '-' + day.split('"close": "')[1].split('"')[0]
                        if hours == '':
                            hours = dname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dname + ': ' + hrs
                try:
                    purl = item['URL']
                except:
                    purl = '<MISSING>'
                if store not in ids:
                    ids.append(store)
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
