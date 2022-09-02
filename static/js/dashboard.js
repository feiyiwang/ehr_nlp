var data = [
   {'program':'Breast Oncology','freq':{'<50':0, '50-60':2, '60-70':1, '70-80':2, '80-90':5, '>90':1}}
   ,{'program':'Cutaneous Oncology','freq':{'<50':1, '50-60':1, '60-70':0, '70-80':0, '80-90':0, '>90':0}}
   ,{'program':'Gastrointestinal Oncology','freq':{'<50':1, '50-60':4, '60-70':2, '70-80':1, '80-90':2, '>90':1}}
   ,{'program':'Thoracic Oncology','freq':{'<50':0, '50-60':5, '60-70':1, '70-80':2, '80-90':0, '>90':0}}
   ,{'program':'Hematologic Malignancies','freq':{'<50':1, '50-60':1, '60-70':0, '70-80':1, '80-90':2, '>90':0}}
   ,{'program':'Gynecology Oncology','freq':{'<50':0, '50-60':0, '60-70':0, '70-80':1, '80-90':1, '>90':0}}
];

function dashboard(id, fData){

    d3.select(id + "> svg").remove();
    d3.select(id + "> svg").remove();
    d3.select(id + "> table").remove();
    d3.select(id + "> svg").remove();

    var colors = ["#a6d841", "pink", "coral", "gold","purple", "turquoise", "silver","tan","#e1a5ff"];
    var colorMap = {};

    var opt1_name = '';
    for (var key in fData[0]){
        if(key != 'freq') {opt1_name = key;}
    }

    console.log(opt1_name);
    var freq_keys = Object.keys(fData[0]['freq']);
    console.log(freq_keys);

    // define color
    var barColor = 'steelblue';

    for(var i = 0; i < freq_keys.length; i++){
        colorMap[freq_keys[i]] = colors[i];
    }
    function segColor(c){ return colorMap[c];}
    // function segColor(c){ return {'<50':"coral", '50-60':"mediumseagreen", '60-70':"pink", '70-80':"gold",'80-90':"tan",'>90':"purple"}[c]; }

    // compute total for each state.
    fData.forEach(function(d){
        var total = 0;
        for(var i = 0; i < freq_keys.length; i++){
            total += d['freq'][freq_keys[i]];
        }
        d.total = total;
    });
    // fData.forEach(function(d){d.total=d['freq']['<50']+d['freq']['50-60']+d['freq']['60-70']+d['freq']['70-80']+d['freq']['80-90']+d['freq']['>90'];});

    function wrap(text, width) {
        text.each(function() {
            var text = d3.select(this),
                words = text.text().split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.1, // ems
                y = text.attr("y"),
                dy = parseFloat(text.attr("dy")),
                tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node().getComputedTextLength() > width) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
                }
            }
        });
    }

    // function to handle histogram.
    function histoGram(fD){
        var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
        hGDim.w = 500 - hGDim.l - hGDim.r,
            hGDim.h = 200 - hGDim.t - hGDim.b;

        //create svg for histogram.
        var hGsvg = d3.select(id).append("svg")
            .attr("width", hGDim.w + hGDim.l + hGDim.r)
            .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
            .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

        // create function for x-axis mapping.
        var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
            .domain(fD.map(function(d) { return d[0]; }));

        // Add x-axis to the histogram svg.
        hGsvg.append("g").attr("class", "x axis")
            .attr("transform", "translate(0," + hGDim.h + ")")
            .call(d3.svg.axis().scale(x).orient("bottom"));

        // Create function for y-axis map.
        var y = d3.scale.linear().range([hGDim.h, 0])
            .domain([0, d3.max(fD, function(d) { return d[1]; })]);

        // Create bars for histogram to contain rectangles and freq labels.
        var bars = hGsvg.selectAll(".bar").data(fD).enter()
            .append("g").attr("class", "bar");

        //create the rectangles.
        bars.append("rect")
            .attr("x", function(d) { return x(d[0]); })
            .attr("y", function(d) { return y(d[1]); })
            .attr("width", x.rangeBand())
            .attr("height", function(d) { return hGDim.h - y(d[1]); })
            .attr('fill',barColor)
            .on("mouseover",mouseover)// mouseover is defined below.
            .on("mouseout",mouseout);// mouseout is defined below.

        //Create the frequency labels above the rectangles.
        bars.append("text").text(function(d){ return d3.format(",")(d[1])})
            .attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
            .attr("y", function(d) { return y(d[1])-5; })
            .attr("text-anchor", "middle");

        function mouseover(d){  // utility function to be called on mouseover.
            // filter for selected state.
            var st = fData.filter(function(s){ return s[opt1_name] == d[0];})[0]
            var nD = freq_keys.map(function(s){ return {type:s, freq:st['freq'][s]} });

            // var st = fData.filter(function(s){ return s['program'] == d[0];})[0],
            //     nD = d3.keys(st['freq']).map(function(s){ return {type:s, freq:st['freq'][s]};});

            // call update functions of pie-chart and legend.
            pC.update(nD);
            leg.update(nD);
        }

        function mouseout(d){    // utility function to be called on mouseout.
            // reset the pie-chart and legend.
            pC.update(tF);
            leg.update(tF);
        }

        // create function to update the bars. This will be used by pie-chart.
        hG.update = function(nD, color){
            // update the domain of the y-axis map to reflect change in frequencies.
            y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

            // Attach the new data to the bars.
            var bars = hGsvg.selectAll(".bar").data(nD);

            // transition the height and color of rectangles.
            bars.select("rect").transition().duration(500)
                .attr("y", function(d) {return y(d[1]); })
                .attr("height", function(d) { return hGDim.h - y(d[1]); })
                .attr("fill", color);

            // transition the frequency labels location and change value.
            bars.select("text").transition().duration(500)
                .text(function(d){ return d3.format(",")(d[1])})
                .attr("y", function(d) {return y(d[1])-5; });
        };
        return hG;
    }

    // function to handle pieChart.
    function pieChart(pD){
        var pC ={},    pieDim ={w:200, h: 200};
        pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

        // create svg for pie chart.
        var piesvg = d3.select(id).append("svg")
            .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
            .attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");

        // create function to draw the arcs of the pie slices.
        var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

        // create a function to compute the pie slice angles.
        var pie = d3.layout.pie().sort(null).value(function(d) { return d['freq']; });

        // Draw the pie slices.
        piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
            .each(function(d) { this._current = d; })
            .style("fill", function(d) { return segColor(d.data.type); })
            .on("mouseover",mouseover).on("mouseout",mouseout);

        // create function to update pie-chart. This will be used by histogram.
        pC.update = function(nD){
            piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                .attrTween("d", arcTween);
        }
        // Utility function to be called on mouseover a pie slice.
        function mouseover(d){
            // call the update function of histogram with new data.
            hG.update(fData.map(function(v){
                return [v[opt1_name],v.freq[d.data.type]];}),segColor(d.data.type));

            // hG.update(fData.map(function(v){
            //     return [v['program'],v['freq'][d.data.type]];}),segColor(d.data.type));
        }
        //Utility function to be called on mouseout a pie slice.
        function mouseout(d){
            // call the update function of histogram with all data.
            hG.update(fData.map(function(v){
                return [v[opt1_name],v.total];}), barColor);

            // hG.update(fData.map(function(v){
            //     return [v['program'],v.total];}), barColor);
        }
        // Animating the pie-slice requiring a custom function which specifies
        // how the intermediate paths should be drawn.
        function arcTween(a) {
            var i = d3.interpolate(this._current, a);
            this._current = i(0);
            return function(t) { return arc(i(t));    };
        }
        return pC;
    }

    // function to handle legend.
    function legend(lD){
        var leg = {};

        // create table for legend.
        var legend = d3.select(id).append("table").attr('class','legend');

        // create one row per segment.
        var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

        // create the first column for each segment.
        tr.append("td").append("svg").attr("width", '12').attr("height", '12').append("rect")
            .attr("width", '12').attr("height", '12')
            .attr("fill",function(d){ return segColor(d.type); });

        // create the second column for each segment.
        tr.append("td").text(function(d){ return d.type;});

        // create the third column for each segment.
        tr.append("td").attr("class",'legendFreq')
            .text(function(d){ return d3.format(",")(d.freq);}); //d['freq']

        // create the fourth column for each segment.
        tr.append("td").attr("class",'legendPerc')
            .text(function(d){ return getLegend(d,lD);});

        // Utility function to be used to update the legend.
        leg.update = function(nD){
            // update the data attached to the row elements.
            var l = legend.select("tbody").selectAll("tr").data(nD);

            // update the frequencies.
            l.select(".legendFreq").text(function(d){ return d3.format(",")(d.freq);}); //d['freq']

            // update the percentage column.
            l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});
        }

        function getLegend(d,aD){ // Utility function to compute percentage.
            return d3.format("%")(d.freq/d3.sum(aD.map(function(v){ return v.freq; }))); //d['freq']  v['freq']
        }

        return leg;
    }

    // calculate total frequency by segment for all state.
    var tF = freq_keys.map(function(d){
        return {type:d, freq: d3.sum(fData.map(function(t){ return t.freq[d];}))};
    });

    // var tF = ['<50', '50-60', '60-70', '70-80', '80-90', '>90'].map(function(d){
    //     return {type:d, freq: d3.sum(fData.map(function(t){ return t['freq'][d];}))};
    // });

    // calculate total frequency by state for all segment.
    var sF = fData.map(function(d){ return [d[opt1_name],d.total]});
    // var sF = fData.map(function(d){return [d['program'],d.total];});

    function blankBox() {
        var box = d3.select(id).append("svg")
            .attr("width",40)
            .attr("height", 200)
    }

    var pC = pieChart(tF), bB = blankBox(), leg= legend(tF), hG = histoGram(sF);
}