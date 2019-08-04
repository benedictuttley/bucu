
// Create data array of values to visualize
// Create variable for the SVG
var svg = d3.select("body").append("svg")
          .attr("height","100%")
          .attr("width","100%");

// Select, append to SVG, and add attributes to rectangles for bar chart
svg.selectAll("rect")
    .data(dataArray)
    .enter().append("rect")
          .attr("class", "bar")
          .attr("height", function(d, i) {return (d / 10)})
          .attr("width","40")
          .attr("x", function(d, i) {return (i * 60) + 25})
          .attr("y", function(d, i) {return 400 - (d / 10)});

