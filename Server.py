# Set up the flask app
from flask import Flask, request, render_template, jsonify
import requests
import xmltodict, json
from xmljson import badgerfish as bf
import xml.etree.ElementTree as ET
import sys
import time

# Inputs: Disease term, time-span
# Outputs: Number of related articles per time unit for length of time-span

# Thoughts?
# Find time unit of request [CHECK]
# Accept list of years from user [CHECK]
# Compare esearch & efectch [check]
# 2 step process, 1st search then fetch [CHECK]
# Attempt fetch with XML for larger bandwidth [CHECK]
# Need to find query key and webenv [CHECK]
# Scope request to years specified by user [CHECK]
# When data is returned, build UI and d3js charts [CHECK]
# Setup Heroku app []

app = Flask(__name__, static_url_path='') 

@app.route('/form')
def hello():
    return render_template('index.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/results', methods=["GET", "POST"])
def index():
    disease_of_interest = request.form['disease']
    start_date = int(request.form['startYear']) # Extract start year from form
    end_date = int(request.form['endYear']) # Extract end year from form
    print("User Input")
    print("Disease of interest: " + disease_of_interest)
    print("Start Date: " + str(start_date))
    print("End Date: " + str(end_date))

     # Build the query:
    query = constructSearch(disease_of_interest, start_date, end_date)
    response = requests.get(query)
    response = json.loads(response.text)
    
    # Extract webenv and query_key
    webenv = response.get("esearchresult").get("webenv")
    querykey = response.get("esearchresult").get("querykey")

    #constructFetch(webenv, querykey)

    recordsPerYear = [0] * ((end_date - start_date) + 1)

    # Perform a batch query
    batchsize = 10000 # Max batch size seems to be 10,000
    recordsToRetieve = int(response.get("esearchresult").get("count")) # int conversion for use in loop
    print("records to retieve:" + recordsToRetieve)
    for i in range(0, recordsToRetieve, batchsize):
        query = constructFetch(webenv, querykey, batchsize, i) # Limited to x per second without account
        try:
            response = requests.get(query)
        except:
            time.sleep(15)
            response = requests.get(query)
        
        root = ET.fromstring(response.text)

        for docsum in root.findall('DocSum'):
            pubdate = docsum.find('Item').text
            pubdate = pubdate.split(" ")[0]

            if (pubdate.isdigit()):
                pubdate  = int(pubdate)
                if(pubdate <= end_date and pubdate >= start_date):
                    index = end_date - pubdate
                    recordsPerYear[index] = recordsPerYear[index] + 1 # insert at index (max-year - current year)


    data = constructDataObject(start_date, end_date, recordsPerYear)
    dataToSend = {"data": data}
    return render_template("results.html", data=dataToSend) #render_template("results.html", data=data)

# Retrieve ID's for resources with publication date in user specified range
def constructSearch(disease_of_interest: str, startDate: str, endDate: str):
    query = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + disease_of_interest + "&usehistory=y&mindate=" + str(startDate) + "&maxdate=" +str(endDate) + "&datetype=pdat&retmax=0&retmode=json"
    return query

# Fetch next chunk of records
def constructFetch(webenv: str, querykey: str, recordsToRetieve:int, startingRecord:int):    
    query = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&api_key=c0ace8ea2769fdd119319f4bc21692b21308&webEnv=" + webenv + "&query_key=" + querykey + "&retmode=xml&retmax=" + str(recordsToRetieve) + "&retstart=" + str(startingRecord)
    return query


# Create JSON for passing to template
def constructDataObject(startYear: int, endYear: int, records: list):
    data = []
    timeSpan = endYear-startYear + 1
    for i in range(0, timeSpan):
        data.append({"year":startYear+i, "frequency":records[i]})
    return data