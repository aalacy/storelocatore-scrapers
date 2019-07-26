const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'http://littlegeneral.com/Locations.html';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
 
        const $  =cheerio.load(html);
        var items=[];
      var script =  $('script[type="text/javascript"]').html();
      var script1 = Array(script).toString();
      var script2 = script1.split(';');
     var script3 = script2[0];
     var script4 = script3.split('],');
    
     function mainhead(i)

        {
          if(42>i)

            {
 
        var script5 = script4[i];
        var script6 = script5.split('<br>');
        var script8 = script6[1];
        
       

                                  if(script6.length==5){
                                    var address = script6[1].trim();
                                    var city_tmp = script6[2];
                                    var city_tmp1 = city_tmp.split(',');
                                    var city = city_tmp1[0].trim();
                                    var state_tmp = city_tmp1[1];
                                    var state_tmp1 = state_tmp.split(' ');
                                    var  phone =script6[3].trim();
                                    var latitude_tmp = script6[4];
                                    var latitude_tmp1 = latitude_tmp.split(',');
                                    var latitude = latitude_tmp1[1].trim();
                                    var longitude = latitude_tmp1[2].trim();
                                    var location_name_tmp = script6[0];
                                    var location_name = location_name_tmp.replace('<strong>','').replace('[','').replace('</strong>','').replace(' var locations = ','').replace('[','').replace(" '","").trim();
                                    var store_number_tmp = location_name.split('#');
                                    var store_number = store_number_tmp[1].trim();
                                    if(state_tmp1.length == 4){
                                      var state = state_tmp1[1].trim();
                                      var zip = state_tmp1[2].trim();
                                  }
                                  else if (state_tmp1.length == 2){
                                      var state = state_tmp1[0].trim();
                                      var zip = state_tmp1[1].trim();
                                  }
                                  else if (state_tmp1.length == 3){
                                  var state = state_tmp1[1].trim();
                                  var zip = state_tmp1[2].trim();
                              }

                                  
                                    
                                  }
                                  else if(script6.length == 4){

                                      var tmpaddress =  script5;
                                      var tmpaddress1 =tmpaddress.split('<br>');
                                      var tmpaddres2 = tmpaddress1[1]; 
                                      var tmpaddres3 = tmpaddres2.split(',');
                                      var tmpaddres4 =  tmpaddres3[0];
                                      var tmpaddres5 = tmpaddres4.split(' ');
                                      var tmpaddres6 = tmpaddres5[1] + ' ' +   tmpaddres5[2] + ' ' + tmpaddres5[3];
                                      var city = tmpaddres5[4].trim();
                                      var state_tmp =tmpaddres3[1];
                                      var state_tmp1 = state_tmp.split(' ');
                                      var state = state_tmp1[1].trim();
                                      var zip = state_tmp1[2].trim();
                                      var phone = tmpaddress1[2].trim();
                                      var latitude_tmp = script6[3];
                                      var latitude_tmp1 = latitude_tmp.split(',');
                                      var latitude = latitude_tmp1[1].trim();
                                      var longitude = latitude_tmp1[2].trim();
                                      var location_name_tmp = script6[0];
                                      var location_name = location_name_tmp.replace('<strong>','').replace('[','').replace('</strong>','').replace(' var locations = ','').replace('[','').replace(" '","").trim();
                          
                                      var store_number_tmp = location_name.split('#');
                                      var store_number = store_number_tmp[1].trim();
                                      var address = tmpaddres6.trim(); 
                                      
                                  }
                                  

                                  items.push({  

                                      locator_domain: 'http://littlegeneral.com/', 

                                      location_name: location_name, 

                                      street_address: address,

                                      city: city, 

                                      state: state,

                                      zip:  zip,

                                      country_code: 'US',

                                      store_number: store_number,

                                      phone: phone,

                                      location_type: 'littlegeneral',

                                      latitude: latitude,

                                      longitude: longitude, 

                                      hours_of_operation:'<MISSING>'}); 
                                      
                                      
                            
                                      mainhead(i+1);
       
   
    } 

    else{
   
      resolve(items);
  
     }
  } 
  
  mainhead(0);
  }
});
});

}

Apify.main(async () => {

    

  const data = await scrape();
  

   await Apify.pushData(data);

});
