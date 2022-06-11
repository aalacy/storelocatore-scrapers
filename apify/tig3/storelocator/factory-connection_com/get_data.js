const axios = require('axios');
const pako = require('pako');
const atob = require('atob');

async function getData() {
  let page_url =
    'https://app.locatedmap.com/initwidget/?instanceId=fb5794db-1003-4eb9-8d61-3912f1b0e26a&compId=comp-k2z7snsm&viewMode=site&styleId=style-k2z7svc0';
  let response = await axios.get(page_url);
  let locData = new Uint8Array(
    atob(response.data.locations.base64)
      .split('')
      .map(function (x) {
        return x.charCodeAt(0);
      })
  );
  let locations = JSON.parse(pako.inflate(locData, { to: 'string' }));
  console.log(JSON.stringify(locations));
}

getData();
