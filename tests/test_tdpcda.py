#Testing
import tdpcda.tdpcda as cda
import pytest

#Global variables
resultid = None

def check_uuid(uuid):
    uuidresult = cda.checkUUID(uuid)
    return uuidresult

def test_testUUID():
    posuuid = "6396cba4-fa75-4336-afc9-c73eef9977bd"
    neguuid = "Farfromgroovin"
    posresult = check_uuid(posuuid)
    assert posresult == True
    negresult = check_uuid(neguuid)
    assert negresult == False

def get_Projects(testdata):
    projdata = cda.getProjects(testdata)
    return projdata

def test_getProjects():
    projdata = get_Projects(True)
    assert projdata == ["TCGA-UCS", "TCGA-OV", "TCGA-GBM","TCGA-KICH", "TCGA-KIRC", "TCGA-BRCA"]
    fullprojdata = get_Projects(False)
    #assert "TARGET-AML" in fullprojdata == True
    assert fullprojdata.count("TARGET-AML") > 0

def checkQuery(query):
    resultid = cda.runCDASQLQuery(query)
    return resultid


def test_CDAquery():
    projectquery = """SELECT DISTINCT(_project) FROM gdc-bq-sample.cda_mvp.v3, UNNEST(ResearchSubject) AS _ResearchSubject, UNNEST(_ResearchSubject.Specimen) AS _Specimen, UNNEST(_Specimen.File) AS _File, UNNEST(_File.associated_project) as _project"""
    global resultid
    resultid = checkQuery(projectquery)
    isuuid = check_uuid(resultid)
    assert isuuid == True

def getJobStatus(uuid):
    status = cda.checkJobStatus(uuid)
    return status['done']

def test_JobStatus():
    status = getJobStatus(resultid)
    assert status == True

def getResults(uuid):
    resultset = cda.getResults(uuid)
    return resultset

def test_getResults():
    resultset = getResults(resultid)
    assert len(resultset) > 0


