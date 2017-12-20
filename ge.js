window.onload = function () {

//chart
var listOfDatapoints = [];



var dataPoints1 = [];
var dataPoints2 = [];
var chart = new CanvasJS.Chart("chartContainer", {
	zoomEnabled: true,
	title: {
		text: "Real Time Volume of Supplies Traded",
		fontFamily: "Arial",
		fontWeight: "Bolder"
	},
	axisX: {
		title: "Real time quantities from OSBuddy GE API",
		fontFamily: "Arial",
	},
	axisY:{
		prefix: "",
		includeZero: false,
		minimum: 0
	}, 
	toolTip: {
		shared: true
	},
	legend: {
		cursor:"pointer",
		verticalAlign: "top",
		fontSize: 18,
		fontFamily: "Arial",
		fontColor: "dimGrey",
		itemclick : toggleDataSeries,
		verticalAlign: "top",
		horizontalAlign: "center"
	},
	data: [{ 
		type: "line",
		color: "#C3C850",
		lineColor: "#C3C850",
		xValueType: "dateTime",
		yValueFormatString: "####.00",
		xValueFormatString: "hh:mm:ss TT",
		fontFamily: "Arial",
		showInLegend: true,
		name: "Saradomin Brew(4)",
		dataPoints: dataPoints1
		},
		{				
			type: "line",
			color: "#65D7A9",
			lineColor: "#65D7A9",
			xValueType: "dateTime",
			yValueFormatString: "####.00",
			fontFamily: "Arial",
			showInLegend: true,
			name: "Prayer Potion(4)" ,
			dataPoints: dataPoints2
	}]
});


var dataPoints3 = [];
var dataPoints4 = [];
var chart2 = new CanvasJS.Chart("chartContainer2", {
	zoomEnabled: true,
	title: {
		text: "Real Time Prices of Supplies Traded",
	    fontFamily: "Arial",
	    fontWeight: "Bolder"

	},
	axisX: {
		title: "Real time prices from OSBuddy GE API",
		fontFamily: "Arial"

	},
	axisY:{
		prefix: "",
		includeZero: false,
		minimum: 0
	}, 
	toolTip: {
		shared: true
	},
	legend: {
		cursor:"pointer",
		verticalAlign: "top",
		fontSize: 18,
		fontFamily: "Arial",
		fontColor: "dimGrey",
		itemclick : toggleDataSeries
	},
	data: [{ 
		type: "line",
		color: "#C3C850",
		lineColor: "#C3C850",
		xValueType: "dateTime",
		yValueFormatString: "####.00",
		xValueFormatString: "hh:mm:ss TT",
		fontFamily: "Arial",
		showInLegend: true,
		name: "Saradomin Brew(4)",
		dataPoints: dataPoints3
		},
		{				
			type: "line",
			color: "#65D7A9",
			lineColor: "#65D7A9",
			xValueType: "dateTime",
			yValueFormatString: "####.00",
			showInLegend: true,
			name: "Prayer Potion(4)" ,
			dataPoints: dataPoints4
	}]
});

var dataPoints5 = [];
var chart3 = new CanvasJS.Chart("chartContainer3", {
	zoomEnabled: true,
	title: {
		text: "OSRS Current Population",
		fontFamily: "Arial",
		fontWeight: "Bolder"
	},
	axisX: {
		title: "Real time population from OSRS Website",
		fontFamily: "Arial",
	},
	axisY:{
		prefix: "",
		includeZero: false,
		minimum: 0
	}, 
	toolTip: {
		shared: true
	},
	legend: {
		cursor:"pointer",
		verticalAlign: "top",
		fontSize: 18,
		fontFamily: "Arial",
		fontColor: "dimGrey",
		itemclick : toggleDataSeries,
		verticalAlign: "top",
		horizontalAlign: "center"
	},
	data: [{ 
		type: "line",
		color: "red",
		lineColor: "red",
		lineDashType: "dashed",
		xValueType: "dateTime",
		yValueFormatString: "####.00",
		xValueFormatString: "hh:mm:ss TT",
		fontFamily: "Arial",
		showInLegend: true,
		name: "Current Population",
		dataPoints: dataPoints5
		}]
});


function toggleDataSeries(e) {
	if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
		e.dataSeries.visible = false;
	}
	else {
		e.dataSeries.visible = true;
	}
}

// how fast values update on graph
var updateInterval = 1500;
var time = new Date;

function updateChart(count) {
	count = count || 1;
	for (var i = 0; i < count; i++) {
		time.setTime(time.getTime()+ updateInterval);
	// pushing the new values
	httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=6685", get1);
    httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=2434", get2);

    httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=6685", get3);
    httpGet("https://api.rsbuddy.com/grandExchange?a=guidePrice&i=2434", get4);

    //population chart
    updatePopulation();
    //console.log(dataPoints1.length);
    if (dataPoints1.length > 1){
    	//console.log("it gets here!!!")
      	dataPoints1.shift();
      	dataPoints2.shift();
      	dataPoints3.shift();
      	dataPoints4.shift();				
      }
	}
	// if (dataPoints1.length > 1)
	// {
	// 	dataPoints1.shift();	
	// 	dataPoints2.shift();			
	// }
	// updating legend text with  updated with y Value 
	// chart.options.data[0].legendText = " Death Rune  GP: " + yValue1;
	// chart.options.data[1].legendText = " Blood Rune  GP:" + yValue2; 
	chart.render();
	chart2.render();
	chart3.render();

}
// generates first set of dataPoints 
updateChart(100);	
setInterval(function(){updateChart()}, updateInterval);

function httpGet(theUrl, callBack)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, true ); // false for synchronous request
    xmlHttp.onreadystatechange = function() {
   	if (this.responseText && this.status == 200) {
    		callBack(JSON.parse(this.responseText));
    	}
    }
    xmlHttp.send( null );
}

function get1(item) {
	chart.options.data[0].legendText = " Saradomin Brew(4) - QTY TRADED: " + String(item.sellingQuantity);
	dataPoints1.push({
	x: time.getTime(),
	y: item.sellingQuantity
	});
}
function get2(item) {
	chart.options.data[1].legendText = " Prayer Potion(4) - QTY TRADED: " + String(item.sellingQuantity); 
	dataPoints2.push({
	x: time.getTime(),
	y: item.sellingQuantity
	});
}

function get3(item) {
	chart2.options.data[0].legendText = " Saradomin Brew(4) - MARKET PRICE: " + String(item.selling);
	dataPoints3.push({
	x: time.getTime(),
	y: item.selling
	});
}
function get4(item) {
	chart2.options.data[1].legendText = " Prayer Potion(4) - MARKET PRICE: " + String(item.selling);
	dataPoints4.push({
	x: time.getTime(),
	y: item.selling
	});
}









function updatePopulation() {
	var request = require('request'),
	cheerio = require('cheerio');

	request('http://localhost:8000/?other=http://www.oldschool.runescape.com', function(err, resp, body){
	if (!err && resp.statusCode == 200) {
		var $ = cheerio.load(body);
		var playerCount = $('.player-count');
		var playerCountTextSplit = (playerCount.text().split(" "));
		var playerCountInt = parseInt(playerCountTextSplit[3]);
		
		chart3.options.data[0].legendText = " USERS ONLINE: " + String(playerCountInt);
		dataPoints5.push({
		x: time.getTime(),
		y: playerCountInt
		});
		// console.log(playerCountInt);
	}
	});
}


}