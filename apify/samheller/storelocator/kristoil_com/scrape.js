const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: 'GET',
    url: 'http://www.kristoil.com/locations/'
  }).then((resp) => {
    doc = new JSDOM(resp.data).window.document;
    returnData = [];
    for (let row of doc.querySelectorAll('tr')){
      data = row.querySelectorAll('td');
      if (data.length == 0){continue;} //ignore anything w/o TDs (prolly table headers)
        address = data[1]
          .textContent
          .replace('St. Germain', 'Saint Germain,')
          .replace(' St. ', ' St., ')
          .replace(' St ', ' St., ')
          .replace('Dr.', 'Dr.,')
          .replace('Ave.', 'Ave.,')
          .replace(' Ave ', ' Ave., ')
          .replace(' Avenue ', ' Avenue, ')
          .replace('Rd.', 'Rd.,')
          .replace('Highway 41', 'Highway 41,')
          .replace('Highway 2', 'Highway 2,')
          .replace('Hwy 70,', 'Hwy 70')
          .replace(', P.O', ' P.O')
          .replace(', Box', ' Box')
          .replace('Charlevoix MI', 'Charlevoix, MI')
          .replace('US 41 ', 'US 41, ')
          .replace(' Road ', ' Road, ')
          .replace('Green Bay WI', 'Green Bay, WI')
          .replace(', B Box', ' B Box')
          .replace(', Box', ' Box')
        address = sanitize(address)


        area = address[2].split(' ')
        if (area.length == 1){area.push('<MISSING>')}
        zip = area.pop();
        state = area.join(' ');
        if (state == 'Wells'){
          console.log(address, state, zip, area)
        }

        returnData.push({
          locator_domain: 'kristoil.com',
          location_name: '<MISSING>',
          street_address: address[0],
          city: address[1],
          state: state,
          zip: zip,
          country_code: 'US',
          store_number: '<MISSING>',
          phone: data[2].textContent,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: '<MISSING>'
        })
    }
    return returnData;
  })
}

function sanitize(textRow){
  sane = [];
  for (s of textRow.split(",")){
    s = s.replace(/^\./, '').replace(/\.$/, '')
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
}

