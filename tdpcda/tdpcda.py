#Library of routines I use for CDA
import requests
import uuid


def getProjects(testmode=True):   
    """ 
    Returns a list of projects in CDA.  If testmode is True, a set of 6 projects is returned.  If False, all projects are returned  

    :param testmode 

    :type testmode: boolean 

    """ 

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
    """ 
    Run a SQL query using the CDA SQL endpoint and return the query id  

    :param querystring  

    :type querystring: str  

    """ 

    cdaURL = 'https://cda.cda-dev.broadinstitute.org/api/v1/sql-query'  
    headers = {'accept' : 'application/json', 'Content-Type' : 'text/plain'}    

    request = requests.post(cdaURL, headers = headers, data = querystring)  

    if request.status_code == 200:  
        result = request.json() 
        query_id = result['query_id']   
        return query_id
    else:   
        raise Exception ("Query failed code {}. {}".format(request.status_code))    

def checkUUID(teststring): 
    """ 
    Tests if a string is a UUID or not.  Returns boolean.   

    :param teststring   
    :type teststring: str   

    """ 
    try:    
        uuid.UUID(teststring)   
        return True 
    except ValueError:  
        return False    


def checkJobStatus(queryid):  
    """ 
    Checks on the job status for the provide query ID. Returns a JSON object: {"done" : True/False, "status" : returned status, "runningTime" : returned running time}  

    :param queryid  
    :type queryid string    

    """ 
    cdaURL = "https://cda.cda-dev.broadinstitute.org/api/v1/job-status/{}".format(queryid)  
    headers = {'accept' : 'application/json'}   

    parseddata = {} 

    request = requests.get(cdaURL, headers = headers)   

    if request.status_code == 200:  
        data = request.json()   
        status = data['status'] 
        runningTime = data['runningTime']   
        if "state=DONE" in status: 
            parseddata['done'] = True   
        else:   
            parseddata['done'] = False  
        parseddata['status'] = status   
        parseddata['runningTime'] = runningTime 
        return parseddata   
    else:   
        raise Exception("Query failed code {}. {}".format(request.status_code)) 


def getResults(queryid, offset=0, limit=100): 
    """ 
    Takes either a CDA query ID or a CDA next_url and returns the data in a JSON object: {"next_url" : next URL or None, "result" : query result as JSON object}    
    optional offset and limit values can be used to adjust returned data.  Returns None if query hasn't fininshed.  

    :param queryid  
    :type queryid: string   

    :param offset   
    :type offset: int   

    :param limit    
    :type limit: int    


    """ 

    #EXAMPLE call:  curl -X GET "https://cda.cda-dev.broadinstitute.org/api/v1/query/bcff531e-0ada-4d43-9d81-ae9ab05efacb?offset=10&limit=100" -H "accept: application/json"    
    # TODO Check on job status before requesting results in case the query is long-running.  Only applicable if UUID is provided, if next url clearly the job is done   

    if checkUUID(queryid):   
        resultURL = "https://cda.cda-dev.broadinstitute.org/api/v1/query/{}?offset={}&limit={}".format(queryid, str(offset), str(limit))    
    else:   
        resultURL = queryid 

    headers = {'accept' : 'application/json'}   
    returneddata = {}   

    check = checkJobStatus(queryid)   

    if check['done']:   
        request = requests.get(resultURL, headers = headers)    

        if request.status_code == 200:  
            rawdata = request.json()    
            returneddata['next_url'] = rawdata['next_url']  
            returneddata['result'] = rawdata['result']  
            return returneddata 
        else:   
            raise Exception ("Query failed code {}. {}".format(request.status_code))    
    else:   
        return None 