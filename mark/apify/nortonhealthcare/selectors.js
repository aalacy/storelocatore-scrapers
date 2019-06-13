const locationNameSelector = '#cphMain_ihPageTitle';
const checkAddressExists = '#location_PublicDetailView_tab > div.ng-scope > div.row > div > div > div > div > div > div > ih-static-zone > div > div.col-xs-12.col-md-5 > div.form-group.ih-field-locationaddress1';
const streetAddressSelector = '.ih-field-locationaddress1 > div';
const streetAddress2Selector = '.ih-field-locationaddress2 > div';
const citySelector = '.ih-field-locationcity > div';
const stateSelector = '.ih-field-locationstate > div';
const zipSelector = '.ih-field-locationpostalcode > div';
const phoneSelector = '#location_PublicDetailView_tab > div.ng-scope > div.row > div > div > div > div > div > div > ih-static-zone > div > div.col-xs-12.col-md-4 > div.form-group.ih-field-locationphone > div > a';
const mapButtonSelector = '#location_PublicDetailView_tab > div.ng-scope > div.stacked > ih-tabbed-zone > div > div > div.tab-pane.ng-scope.active > div > div > div > a';
const linkSelector = '#location_PublicDetailView_tab > div.ng-scope > div.stacked > ih-tabbed-zone > div > div > div > div > div > div > div:nth-child(3) > div > div > div:nth-child(3) > a';
const hourSelector = '.ih-field-locationhours';

module.exports = {
  locationNameSelector,
  checkAddressExists,
  streetAddressSelector,
  streetAddress2Selector,
  citySelector,
  stateSelector,
  zipSelector,
  phoneSelector,
  mapButtonSelector,
  linkSelector,
  hourSelector,
};
