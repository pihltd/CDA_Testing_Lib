#Library of routines I use for CDA
import requests
import pprint

def getProjects(testmode):
    #Returns a list of projects in CDA.  If testmode is True, will return a list of 5 projects.  If false, will query for all projects known to CDA
    if testmode:
        projectlist = ["TCGA-UCS", "TCGA-OV", "TCGA-GBM","TCGA-KICH", "TCGA-KIRC", "TCGA-BRCA"]
        #projectlist = ["TCGA-BRCA"]
    else:
        projectquery = """SELECT DISTINCT(_project) FROM gdc-bq-sample.cda_mvp.v3, UNNEST(ResearchSubject) AS _ResearchSubject, UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_Specimen.File) AS _File, UNNEST(_File.associated_project) as _project"""
        try:
            resultsid = runCDASQLQuery(projectquery)
        except Exception as e:
            raise(e)

        projresults = getResults(resultsid,0,100)
        projectlist = []
        for projresult in projresults['result']:
            projectlist.append(projresult['_project'])
    return projectlist

def runCDASQLQuery(querystring):
    #Runs a SQL query on the CDA API and returns the result ID
    cdaURL = 'https://cda.cda-dev.broadinstitute.org/api/v1/sql-query'
    headers = {'accept' : 'application/json', 'Content-Type' : 'text/plain'}

    request = requests.post(cdaURL, headers = headers, data = querystring)

    if request.status_code == 200:
        result = request.json()
        query_id = result['query_id']
        return query_id
    else:
        raise Exception ("Query failed code {}. {}".format(request.status_code))