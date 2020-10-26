import csv
import os
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pret_co_uk')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Cookie': 'statePreference=; statePreference=; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb; _ga=GA1.3.682867871.1588958973; _gid=GA1.3.711697636.1588958973; _fbp=fb.2.1588958973219.1726351087; _y2=1%3AeyJjIjp7IjEyNDc2NiI6LTE0NzM5ODQwMDAsIjEyNTIxOCI6LTE0NzM5ODQwMDAsIjEyOTQ4NiI6LTE0NzM5ODQwMDAsIjEzMDIxNiI6LTE0NzM5ODQwMDAsIjEzMTc5NCI6LTE0NzM5ODQwMDAsIjEzMjUwOSI6LTE0NzM5ODQwMDAsIm8iOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A99; newsletterPageReferrer=https://www.pret.co.uk/en-gb/find-a-pret/London; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+08+2020+12%3A30%3A37+GMT-0500+(Central+Daylight+Time)&version=5.9.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_48371%3A1%2C0_48370%3A1%2C0_94508%3A1%2C0_94507%3A1%2C0_48372%3A1%2C0_48365%3A1%2C0_48367%3A1%2C0_48366%3A1%2C0_48369%3A1%2C0_48368%3A1%2C8%3A0&AwaitingReconsent=false; newsletterAction=dwell; newsletterDwellTime=56; _yi=1%3AeyJsaSI6bnVsbCwic2UiOnsiYyI6MSwibGEiOjE1ODg5NTkxMjEzNzgsInAiOjUsInNjIjoxMjN9LCJ1Ijp7ImlkIjoiZDA1MDIzNTctZWYxZC00OTlhLThmODAtOWIxMmI5MzVkYmVjIiwiZmwiOiIwIn19%3ALTE0MzE4NDYxMTI%3D%3A99; lastTimestamp=1588959122; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb'
           }

def fetch_data():
    ids = []
    places = ['London','Birmingham','Glasgow','Liverpool','Bristol','Manchester','Sheffield','Leeds','Edinburgh','Leicester','Coventry','Bradford','Cardiff','Belfast','Nottingham','Kingston upon Hull','Newcastle upon Tyne','Stoke on Trent','Southampton','Derby','Portsmouth','Brighton and Hove','Plymouth','Northampton','Reading','Luton','Wolverhampton','Bournemouth','Aberdeen','Bolton','Norwich','Swindon','Swansea','Milton Keynes','Southend on Sea','Middlesbrough','Sunderland','Peterborough','Warrington','Oxford','Huddersfield','Slough','York','Poole','Cambridge','Dundee','Ipswich','Telford','Gloucester','Blackpool','Birkenhead','Watford','Sale','Colchester','Newport','Solihull','High Wycombe','Exeter','Gateshead','Cheltenham','Blackburn','Maidstone','Chelmsford','Basildon','Salford','Basingstoke','Worthing','Eastbourne','Doncaster','Crawley','Rotherham','Rochdale','Stockport','Gillingham','Sutton Coldfield','Woking','Wigan','Lincoln','St Helens','Oldham','Worcester','Wakefield','Hemel Hempstead','Bath','Preston','Rayleigh','Barnsley','Stevenage','Southport','Hastings','Bedford','Darlington','Halifax','Hartlepool','Chesterfield','Grimsby','Nuneaton','Weston super Mare','Chester','St Albans','Harlow','Guildford','Stockton on Tees','Aylesbury','Derry','Bracknell','Dudley','Redditch','Batley','Scunthorpe','Burnley','Eastleigh','Chatham','Mansfield','Bury','Newcastle under Lyme','Paisley','West Bromwich','South Shields','Carlisle','East Kilbride','Burton upon Trent','Tamworth','Gosport','Shrewsbury','Crewe','Ashford','Rugby','Harrogate','Grays','Lowestoft','Atherton','Stafford','Walsall','Bognor Regis','Cannock','Tynemouth','Bamber Bridge','Walton on Thames','Washington','Farnborough','Rochester','Maidenhead','Paignton','Dewsbury','Filton','Newtownabbey','Loughborough','Margate','Craigavon','Stourbridge','Hereford','Widnes','Wrexham','Taunton','Canterbury','Runcorn','Bangor','Ellesmere Port','Scarborough','Wallasey','Royal Tunbridge Wells','Corby','Halesowen','Kettering','Aldershot','Gravesend','Bebington','Littlehampton','Royal Leamington Spa','Kidderminster','Livingston','Macclesfield','Barry','Christchurch','Altrincham','Weymouth','Brentwood','Hamilton','Ewell','Keighley','Beeston (Broxtowe)','Dunfermline','Folkestone','Clacton on Sea','Willenhall','Sittingbourne','Smethwick','Wellingborough','Welwyn Garden City','Bootle','Lancaster','Esher','Durham','Neath','Kingswinford','Bloxwich','Shoreham by Sea','Cumbernauld','Torquay','Carlton (Gedling)','Horsham','Kirkcaldy','Crosby','Kings Lynn','Horndean','Swadlincote','Hinckley','Bridgend','Sutton in Ashfield','Yeovil','Winchester','Banbury','Perth','West Bridgford','Inverness','Cheshunt','Cwmbran','Ashton under Lyne','Havant','Ayr','Kilmarnock','Northwich','Locks Heath','Wokingham','Andover','Salisbury','Lisburn','Barrow in Furness','Wallsend','Tipton','Merthyr Tydfil','Llanelli','Grantham','Boston','Hatfield','Lytham St Annes','Hoddesdon','Bridgwater','Dover','Middleton (Rochdale)','Bexhill','Coatbridge','Jarrow','Fareham','Kirkby','Braintree','Trowbridge','Greenock','Worksop','Ramsgate']
    for place in places:
        logger.info(('Pulling City %s...' % place))
        url = 'https://www.pret.co.uk/en-gb/find-a-pret/' + place
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
        website = 'pret.co.uk'
        typ = 'Restaurant'
        for line in lines:
            if '<div class="panel-heading">' in line:
                hours = ''
                lat = ''
                lng = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                phone = ''
                g = next(lines)
                if '>' in g:
                    name = g.split('>')[1].split('<')[0]
                else:
                    name = next(lines).split('>')[1].split('<')[0]
            if '<address>' in line:
                next(lines)
                g = next(lines)
                h = next(lines)
                i = next(lines)
                j = next(lines)
                k = next(lines)
                if 'United Kingdom ' in k:
                    add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + h.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + i.strip().replace('\t','').replace('\n','').replace('\r','')
                    city = j.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                    state = '<MISSING>'
                    zc = k.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
                elif 'United Kingdom' in j:
                    add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + h.strip().replace('\t','').replace('\n','').replace('\r','')
                    city = i.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                    state = '<MISSING>'
                    zc = j.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
                else:
                    try:
                        add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                        city = h.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                        state = '<MISSING>'
                        zc = i.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
                    except:
                        add = ''
                        city = ''
                        state = '<MISSING>'
                        zc = ''
            if '<div class="map-canvas" data-position="' in line:
                lat = line.split('<div class="map-canvas" data-position="')[1].split(',')[0]
                lng = line.split('<div class="map-canvas" data-position="')[1].split(',')[1].split('"')[0].strip()
            if '<span class="number">Telephone: ' in line:
                phone = line.split('<span class="number">Telephone: ')[1].split('<')[0].strip()
            if '<dt class="opening-hours">' in line:
                day = line.split('<dt class="opening-hours">')[1].split('<')[0]
                g = next(lines)
                if '<dd>' not in g:
                    g = next(lines)
                hrs = day + ': ' + g.split('>')[1].split('<')[0].strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<div class="directions-panel">' in line and add != '':
                loc = '<MISSING>'
                country = 'GB'
                store = '<MISSING>'
                latlng = lat + '|' + lng
                if latlng not in ids:
                    ids.append(latlng)
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
