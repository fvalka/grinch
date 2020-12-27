<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <meta name="description" content="">
    <meta name="author" content="">

    <title>global report</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-1.12.4.min.js" integrity="sha384-nvAa0+6Qg9clwYCGGPpDQLVpLNn0fRaROjHqs13t4Ggj3Ez50XnGQqc/r8MhnRDZ" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/gh/rambaut/figtree.js@db798529/dist/figtree.umd.js"></script>
    <script src="https://d3js.org/d3.v6.min.js"></script>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
    body {
      padding-top: 50px;
      font-family: "ArialNova-Light","HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif;
    }
    table text{
        font-family: "ArialNova-Light","HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif; 
    }
    header {
        display: block;
        text-align: right;
    
    }
    .center {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
        }
    .node-background{
        fill:dimgrey;
        stroke:dimgrey;
    }

    .node circle{
      stroke-width:0;
      cursor:pointer;
      fill:#86b0a6;
      stroke:dimgrey;
      }
    .node circle.selected{
      stroke-width:0;
      cursor:pointer;
      fill:#b08686;
      stroke:dimgrey;
      }

    .node rect{
      stroke-width:2;
      fill:#b08686;
      stroke:dimgrey;
    }
    .svg-tooltip {
        background: rgba(69,77,93,.9);
        border-radius: .1rem;
        color: #fff;
        display: block;
        font-size: 14px;
        max-width: 320px;
        padding: .2rem .4rem;
        position: absolute;
        text-overflow: ellipsis;
        white-space: pre;
        z-index: 300;
        visibility: hidden;
  }
  .tooltip-header {
    font-size: 1.3em;
  }
  .tooltip-key {
    font-weight: bold;
  }
  .branch path{
    stroke-width:2;
    stroke: dimgrey;
    stroke-linejoin:round;
    cursor: pointer;
    }
    .branch.hovered path{
      stroke-width:4;
      stroke: dimgrey;
    }
      .node.hovered circle{
      stroke-width:5;
      stroke: dimgrey
      }
      .node text{
         font-family: "ArialNova-Light","HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif; 
         font-weight: 300;
         font-size: 0.9em;
      }
    /* .starter-template {
      padding: 40px 15px;
      text-align: left;
    } */
    .svg-icon {
    display: inline-flex;
    align-self: center;
    }
    h3{
        font-size: 1em;
    }
    #toTopBtn {
    position: fixed;
    bottom: 26px;
    right: 39px;
    z-index: 98;
    padding: 21px;
    background-color: #86b0a6
    }
    .js .cd-top--fade-out {
        opacity: .5
    }
    .js .cd-top--is-visible {
        visibility: visible;
        opacity: 1
    }

    .js .cd-top {
        visibility: hidden;
        opacity: 0;
        transition: opacity .3s, visibility .3s, background-color .3s
    }

    .cd-top {
        position: fixed;
        bottom: 20px;
        bottom: var(--cd-back-to-top-margin);
        right: 20px;
        right: var(--cd-back-to-top-margin);
        display: inline-block;
        height: 40px;
        height: var(--cd-back-to-top-size);
        width: 40px;
        width: var(--cd-back-to-top-size);
        box-shadow: 0 0 10px rgba(0, 0, 0, .05) !important;
        background: url(https://res.cloudinary.com/dxfq3iotg/image/upload/v1571057658/cd-top-arrow.svg) no-repeat center 50%;
        background-color:#86b0a6;
        background-color: hsla(var(--cd-color-3-h), var(--cd-color-3-s), var(--cd-color-3-l), 0.8)
    }

    .slidecontainer {
      width: 100%;
    }
    .slider {
      -webkit-appearance: none;
      width: 100%;
      height: 15px;
      background: #d3d3d3;
      border-radius: 5px;
      stroke: dimgrey;
      outline: none;
      opacity: 0.7;
      -webkit-transition: .2s;
      transition: opacity .2s;
    }
    .slider:hover {
      opacity: 1; 
    }
    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 25px;
      height: 25px;
      border-radius: 50%; 
      background: #86b0a6;
      stroke: dimgrey;
      cursor: pointer;
    }
    .slider::-moz-range-thumb {
      width: 25px;
      height: 25px;
      border-radius: 50%;
      stroke: dimgrey;
      background: #86b0a6;
      cursor: pointer;
    } 

    .tree-container{
      max-height: 1000px;
      overflow: scroll;
    }
    .label{
      display: none;
    }

    .label.show{
      display: inline;
    }

    .node.hovered .label {
        display:inline;
      }

    div.sticky {
        position: -webkit-sticky; /* Safari */
        position: sticky;
        top: 0;
      }
      .searchbar {
        border-style:solid; 
        border-color: lightgrey; 
        border-radius: 5px; 
        float:right
      }
      .figure-container{
      max-height: 600px;
      background-size: contain;
    }

    @media print {
      .tree-container{
      max-height: none;
      overflow: visible;
      
      }
      
      .slider-block {
        display: none;
      }
      .container {
      padding-right: 1.5cm;
      padding-left: 1.5cm;
      padding-bottom: 1.5cm;
      margin: 1cm;
      min-width: 2200px;
      font-size:2.5vw;
      }
      .searchbar {
        display: none;
      }
      h3{ 
        font-size: 2.5vw;
      }
      h2 {
        font-size: 4vw;
        padding: 1cm;
      }
      h1 {
        font-size: 5vw;
      }
      .command-block {
        display: none;
      }
      pre {
        display: none;
      }
      .tree_svg {
        width: 1200px
      }
      .page-footer {
        display: none;
      }
      .grinch-header {
        text-align: left;
      }
      .content-block, p {
      page-break-inside: avoid;
      }
    }
    

    .node circle{
      stroke-width:0;
      cursor:pointer;
      fill:#5F9C82;
      stroke:#F2E7DC;
      
      }
    .node circle.selected{
      stroke-width:0;
      cursor:pointer;
      fill:#E27E7E;
      stroke:#F2E7DC;
      opacity: 1;
      }
    .node rect{
      stroke-width:2;
      fill:#E27E7E;
      stroke:#F2E7DC;
    }
    .svg-tooltip {
        background: rgba(69,77,93,.9);
        color: #F2E7DC;
  }

  .branch path{
    stroke: #F2E7DC;
    opacity: 0.85;
    }
    .branch.hovered path{
      stroke:#F2E7DC;
      opacity: 1;
    }
      .node.hovered circle{
        stroke:#F2E7DC;
      opacity: 1;
      }
      .node text{
         font-family: "ArialNova-Light","HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif; 
         font-weight: 300;
         font-size: 0.9em;
         color: #F2E7DC;
         fill: #F2E7DC;        
      }

      .scale-bar line {
        stroke: #F2E7DC;
      }
      .scale-bar text{
        fill: #F2E7DC;
        color:  #F2E7DC;
      }
    }

    </style>

  </head>

  <body>
    <script>
      $(document).ready(function() {
        $(window).scroll(function() {
        if ($(this).scrollTop() > 20) {
        $('#toTopBtn').fadeIn();
        } else {
        $('#toTopBtn').fadeOut();
        }
        });
        
        $('#toTopBtn').click(function() {
        $("html, body").animate({
        scrollTop: 0
        }, 400);
        return false;
        });
        });
    </script>
    
    <script type="text/javascript">
      const updateTableFactory = (tooltipId,metadata)=>(tipId)=>{
              const data = metadata[tipId];
              const tableDiv = d3.select(document.getElementById(tooltipId));
              //Remove table
          tableDiv.html("")
              if (data !== undefined) {
                  const visibleData = Object.keys(data).filter(d=>d!=='sequence_name');
                  tableDiv.append("h3")
                      .attr("class",'tooltip-header')
                      .text(tipId)
                      .append("hr");
                  tableDiv.selectAll("p")
                          .data(visibleData)
                          .enter()
                          .append("p")
                          .attr("class","tooltip-text")
                              .selectAll("span")
                              .data(d=>[d,data[d]])
                              .enter()
                              .append("span")
                              .attr("class",(d,i)=> i===0? "tooltip-key" :"tooltip-value")
                              .text((d,i)=>i===0? d + " : ": d);
              }
      }
      <%text>
      
      function addSliderEventHandler(sliderID,fig){
        const svg = fig.svgSelection.select(function() { return this.parentNode; })
        const initialHeight = svg.attr("height");
        const maxHeight = fig.tree().externalNodes.length*50; // 50 pixels for each tip plus a little for margins;

        if(maxHeight<=initialHeight){
          d3.select(`#${sliderID}`).remove();// don't need  a slider
          return;
        }
        const heightScale = d3.scaleLinear()
                .range([initialHeight,maxHeight])
                .domain([0,1])

            if(initialHeight/fig.tree().externalNodes.length>12){
              fig.svgSelection.selectAll(".label")
              .classed("show",true)
            }

        d3.select(`#${sliderID}`).on("input",function(){
              const svgHeight = heightScale(this.value);
              //magic number!!
              svg.attr("height", svgHeight);
            fig.update();
            if(svgHeight/fig.tree().externalNodes.filter(node=>!node[fig.id].ignore).length>12){
              fig.svgSelection.selectAll(".label")
              .classed("show",true)
            }else{
              fig.svgSelection.selectAll(".label")
              .classed("show",false)
            }
        })
      }
      </%text>

      function buildTree(svgID, myTreeString,tooltipID,backgroundDataString,sliderID) {
          const backgroundData = JSON.parse(backgroundDataString);
          const updateTable = updateTableFactory(tooltipID, backgroundData);
          const margins = {top:50,bottom:60,left:100,right:250}
          const svg = d3.select(document.getElementById(svgID))
          svg.selectAll("g").remove();
          const newickString = myTreeString;
          const tree = figtree.Tree.parseNewick(newickString);
          const fig = new figtree.FigTree(document.getElementById(svgID),margins, tree)
          fig.layout(figtree.rectangularLayout)
                  .nodes(figtree.circle()
                                  .filter(n=>!n.children)
                                  .attr("r",8)
                                  .hilightOnHover(20)
                                  .onClick((node,i,n)=>{
                                    updateTable(node.name);
                                    fig.svgSelection.selectAll(".selected").classed("selected",false);
                                    d3.select(n[i]).classed("selected",true);
                                  }),
                          figtree.tipLabel(v=>v.name).attr("dx",10),
                          figtree.rectangle()
                                  .filter(n=>n[fig.id].collapsed)
                                  .attr("width",20)
                                  .attr("height",20)
                  )
                        .nodeBackgrounds(figtree.circle()
                                          .attr("r", 10)
                                .filter(n=>!n.children)
                                        )
                        .branches(figtree.branch()
                                    .hilightOnHover(20) 
                                    .collapseOnClick()
                                    .on("click",()=>{
                                      const svgHeight = fig.svgSelection.select(function() { return this.parentNode; }).attr("height");
                                      if(svgHeight/fig.tree().externalNodes.filter(node=>!node[fig.id].ignore).length>12){
                                        fig.svgSelection.selectAll(".label")
                                          .classed("show",true)
                                      }else{
                                        fig.svgSelection.selectAll(".label")
                                        .classed("show",false)
                                      }
                                    })
                            )
                            .feature(
                                    figtree.scaleBar()
                                      .direction("x")
                                      .length(1/29903)
                                      .x(-60)
                                      .y(-30)
                                      // .y(fig.svgSelection.select(function() { return this.parentNode; }).attr("height")-margins.top-margins.bottom+20)
                                      .title({text:"~1 SNP",
                                      yPadding:10})
                                        )

        addSliderEventHandler(sliderID,fig);

      }
    </script>

    <div class="container">
      <a href="#" id="toTopBtn" class="cd-top text-replace js-cd-top cd-top--is-visible cd-top--fade-out" data-abc="true"></a>
      <div>
        <header class="grinch-header">
            grinch | 
            <small class="text-muted">global report investigating novel coronavirus haplotypes </small>
            <hr>
        </header>
        <h1>New variant report
            <small class="text-muted">${date}</small>
        </h1>
        <br>
        </div>

        <!-- <p class="lead">grinch identified 5 clusters</p> -->
    
    <br>
    <h3><strong>Data source and processing</strong></h3>
    <p> All whole genome SARS-CoV-2 sequences were pulled from GISAID at 2020-12-27 12:19 GMT. The genomes were de-duplicated based on GISAID sequence name – note that the publically available metadata may not fully allow us to de-duplicate by patient. Full data processing pipeline found <a href="https://github.com/cov-lineages/grinch-report" style="color:#86b0a6">here</a>.</p> 
    <p>The sequences were then assigned lineages with pangolin v2.1.3, pangoLEARN version 2020-12-17.</p>
    <p> Pangolin assigns B.1.1.7 to sequences with more than 4 of the 17 defining B.1.1.7 SNPs – defined  <a href="https://virological.org/t/preliminary-genomic-characterisation-of-an-emergent-sars-cov-2-lineage-in-the-uk-defined-by-a-novel-set-of-spike-mutations/563" style="color:#86b0a6">here</a> – and B.1.351 to any sequences with more than 3 of the 5 defining B.1.351 SNPs.</p>

    <h3><strong>Table 1</strong> | Summary of data   <input class="searchbar" type="text" id="myInput" onkeyup="myFunction('myInput','myTable')" placeholder="Search for lineage..." title="searchbar"></h3>
    <table class="table table-striped" id="myTable">
        <tr class="header">
        <th style="width:10%;">Lineage</th>
        <th style="width:10%;">Country</th>
        <th style="width:10%;">Sequence count</th>
        <th style="width:10%;">Earliest sequence</th>
        <th style="width:10%;">Travel history</th>
        </tr>
        % for row in summary_data:
            <tr>
              <td><a href="#${row['Lineage']}" style="color:#86b0a6">${row["Lineage"]}</a></td>
              <td>${row["Countries"]}</td>
              <td>${row["Count"]}</td>
              <td>${row["Earliest date"]}</td>
              <td>${row["Travel history"]}</td>
            </tr>
        % endfor
        </table>

        
        % for row in summary_data:
          <h2 style="color:#86b0a6"><a id = "${row['Lineage']}"></a>Lineage ${row['Lineage']}</h2>
          <p><b>Caveat:</b> Most locations outside the original focus have not reported sustained transmission and many cases have known travel links to the focal location. Increasing numbers of international cases is currently likely due to increased surveillance and vigilance.</p>
          <h3><strong>Table ${row['Lineage']}</strong> | Lineage ${row['Lineage']}</h3>
          <table class="table table-striped">
              <tr class="header">
              <th style="width:30%;">Statistic</th>
              <th style="width:60%;">Information</th>
              </tr>
              <tr>
                  <td>Count</td>
                  <td>${row["Count"]}</td>
              </tr>
              <tr>
                <td>Likely origin</td>
                <td>${row["Likely origin"]}</td>
              </tr>
              <tr>
                <td>SNPs</td>
                <td>${row["SNPs"]}</td>
            </tr>
            </table>
            
        <br>
          % for figure in row["figures"]:
            <div>
              <h3><strong>Figure ${figure["number"]}</strong> | ${figure["name"]}</h3>
              <div class=figure-container>
                ${figure['data']}
            </div>
            </div>
          % endfor
        % endfor
        
        <div></div>
        <h3><strong>Figure 11</strong> | Air traffic from UK by destination</h3>              
        <p>The number of ticketed origin-to-destination journeys from London airports to countries outside the United Kingdom during October 2020.</p> 
        <p>Colours indicate numbers of published genomes of B.1.1.7 deposited on GISAID as of December 26, 2020. Grey bars indicate countries that have reported the presence of the variant but have not yet published B.1.1.7 sequences on GISAID as of the 26-Dec-2020. White bars indicate countries with no reports of B.1.1.7.</p> 
        <p>Flight data come from the International Air Transportation Association that capture anonymized, passenger-level flight itinerary data, comprising both commercial flights and scheduled charter flights. These data account for ~90% of global air travel volumes, with the remaining volumes modelled using market intelligence. We report data from destinations including >5,000 passengers.</p>
        <p>Figure by Kamran Khan, Isaac Bogoch, Alexander Watts, Oliver Pybus, Moritz Kraemer</p>
               <div class=figure-container>
                  <img src="assets/images/Flights_Genomes_26122020.png" alt="Flights from UK" />
              </div>
        </div>

        <script>
          function myFunction(myInput, myTable) {
            var input, filter, table, tr, td, i, txtValue;
            input = document.getElementById(myInput);
            filter = input.value.toUpperCase();
            table = document.getElementById(myTable);
            tr = table.getElementsByTagName("tr");
            for (i = 0; i < tr.length; i++) {
              td = tr[i].getElementsByTagName("td")[0];
              if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                  tr[i].style.display = "";
                } else {
                  tr[i].style.display = "none";
                }
              }       
            }
          }
          </script>
    <footer class="page-footer">
      <div class="container-fluid text-right text-md-right">
        <hr>
        <div class="row">
          <div class="col-sm-1">
            <p>
            <img class="pangolin-logo" src=https://raw.githubusercontent.com/cov-lineages/lineages-website/master/assets/images/pangolin_logo.svg vertical-align="left" width="50" height="50"></img>
            <p>
        </div>

      <div class="col-sm-11" style="text-align: right;">
        grinch ${version} | <small class="text-muted">global report investigating novel coronavirus haplotypes</small> <br><small class="text-muted">GNU General Public License v3.0</small></div>

        <br><br>
        </p>
      </div>
    </footer>
    </div>
    
    

    <script src="https://code.jquery.com/jquery-1.12.4.min.js" integrity="sha384-nvAa0+6Qg9clwYCGGPpDQLVpLNn0fRaROjHqs13t4Ggj3Ez50XnGQqc/r8MhnRDZ" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>
  </body>
</html>
