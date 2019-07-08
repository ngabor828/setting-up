import requests
import json

from rest_framework.response import Response

from bs4 import BeautifulSoup
from lxml import html

class Service:

    ########################################################
    #################### Public methods ####################
    ########################################################

    # Get project id from project code
    # cookie - for authorization
    # projectCode - the code of jira project
    def getProjectId(self, cookie, projectCode):
        try:
            # Prepare url and headers
            url = 'https://cognitivecreators.atlassian.net/rest/api/2/project/' + projectCode
            headers = {'Content-Type': 'application/json', 'Cookie': cookie}

            # Create request
            r = requests.get(url, headers=headers)
            
            # Get responseDict and return id
            responseDict = json.loads(r.text)
        except:
            raise Exception('Project code is not existing')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Project code is not existing')

        return responseDict['id']

    # Setup issue types call
    # cookie - for authorization
    # projectId - the id of jira project
    # projectCode - the code of jira project
    # boardType - type of board
    def setupIssueTypesAndWorkflow(self, cookie, projectId, projectCode, boardType):
        # Get issue types
        issueTypes = self.__getIssueTypes__(cookie, projectCode)

        # Setup issue types
        self.__setupIssueTypes__(cookie, projectId, projectCode, boardType, issueTypes)

        # Add workflow with issue types
        workflowSchemeId = self.__addWorkflowWithIssueTypes__(cookie, projectCode, boardType, self.__addIssueTypesByBoardType__(boardType, []))

        # Publish workflow
        self.__publishWorkflowScheme__(cookie, projectId, workflowSchemeId)

        return Response('{}')

    # Create board call
    # cookie - for authorization
    # json_data - contains the following keys: name, projectIds, preset, locationId, locationType
    def createBoard(self, cookie, json_data):
        try:
            # Prepare url and headers
            url = 'https://cognitivecreators.atlassian.net/rest/greenhopper/1.0/rapidview/create/presets'
            headers = {'Content-Type': 'application/json', 'Cookie': cookie}
            
            # Create request
            r = requests.post(url, json=json_data, headers=headers)
        except:
            raise Exception('Error while creating board')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Error while creating board')

        return r.text

    # Setup filter query call
    # cookie - for authorization
    # projectCode - the code of jira project
    # boardId - id of board
    # boardType - type of board
    def setupFilterQuery(self, cookie, projectCode, boardId, boardType):
        try:
            # Prepare url, json_data and headers
            url = 'https://cognitivecreators.atlassian.net/rest/api/2/filter/' + self.__getFilterQueryId__(cookie, boardId)
            body = self.__getBodyForFilterQueryCall__(boardType, projectCode)
            json_data = json.loads(body)
            headers = {'Content-Type': 'application/json', 'Cookie': cookie}

            # Create request
            r = requests.put(url, json=json_data, headers=headers)
        except:
            raise Exception('Error while setting filter query')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Error while setting filter query')

        return r.text

    # Setup colums call
    # cookie - for authorization
    # boardType - type of board
    # boardId - id of board
    def setupColumns(self, cookie, boardType, boardId):
        try:
            # Prepare url, json_data and headers
            url = 'https://cognitivecreators.atlassian.net/rest/greenhopper/1.0/rapidviewconfig/columns'
            body = self.__getBodyForColumnCall__(boardType, boardId)
            json_data = json.loads(body)
            headers = {'Content-Type': 'application/json', 'Cookie': cookie}

            # Create request
            r = requests.put(url, json=json_data, headers=headers)
        except:
            raise Exception('Error while setting columns')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Error while setting columns')

        return r.text

    # Get board type from name parameter
    # name - name parameter sent from frontend
    def getBoardTypeFromName(self, name):
        return name[int(len(name) - 9):int(len(name) - 6)].replace(' ', '')

    # Get project code from name parameter
    # name - name parameter sent from frontend
    def getProjectCodeFromName(self, name):
        return name[0:name.index(' ')]

    ################ End of Public methods #################

    ########################################################
    ################## Private methods #####################
    ########################################################

    # Get filter query id - function returns the id of the filter query
    # cookie - for authorization
    # boardId - id of board
    def __getFilterQueryId__(self, cookie, boardId):
        # Prepare url and header
        url = 'https://cognitivecreators.atlassian.net/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?rapidViewId=' + boardId
        headers = {'Content-Type': 'application/json', 'Cookie': cookie}

        # Create request
        r = requests.get(url, headers=headers)

        # Convert json string to dictionary
        json_data = json.loads(r.text) 

        return str(json_data['filterConfig']['id'])

    # Define body for setup filter query call
    # boardType - type of board
    # projectCode - the code of jira project
    def __getBodyForFilterQueryCall__(self, boardType, projectCode):
        body = self.__getBodyForFilterQueryCallWithoutProjectCode__(boardType)
        body = body.replace("projectCode", projectCode)
        return body

    # Define body for setup filter query call without project code
    # boardType - type of board
    def __getBodyForFilterQueryCallWithoutProjectCode__(self, boardType):
        switcher = {
            'PO': "{\"jql\":\"project = projectCode AND (type = \\\"PO Task\\\" OR type = \\\"PO Sub-task\\\") ORDER BY Rank ASC\"}",
            'DEV': "{\"jql\":\"project = projectCode AND (type = Bug OR type = \\\"Dev Epic\\\" OR type = \\\"DEV Story\\\" OR type = \\\"DEV Sub-task\\\" OR type = \\\"DEV Task\\\") ORDER BY Rank ASC\"}",
            'MKT': "{\"jql\":\"project = projectCode AND (type = \\\"MKT Task\\\" OR type = \\\"MKT Sub-task\\\") ORDER BY Rank ASC\"}",
            'DSG': "{\"jql\":\"project = projectCode AND (type = \\\"DSG Task\\\" OR type = \\\"DSG Sub-task\\\") ORDER BY Rank ASC\"}"
        }
        return switcher.get(boardType, "")

    # Define body for setup column call
    # boardType - type of board
    # boardId - id of board
    def __getBodyForColumnCall__(self, boardType, boardId):
        body = self.__getBodyForColumnCallWithoutRapidView__(boardType)
        body = body.replace("rapid_view_id", boardId)
        return body

    # Define body for setup column call without rapid view id
    # boardType - type of board
    def __getBodyForColumnCallWithoutRapidView__(self, boardType):
        switcher = {
            'PO': "{\"currentStatisticsField\":{\"id\":\"none_\"},\"rapidViewId\":rapid_view_id,\"mappedColumns\":[{\"mappedStatuses\":[{\"id\":\"1\"}],\"id\":608,\"name\":\"To Do\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"3\"}],\"id\":609,\"name\":\"In Progress\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10001\"}],\"id\":610,\"name\":\"Done\",\"isKanPlanColumn\":false}]}",
            'DEV': "{\"currentStatisticsField\":{\"id\":\"none_\"},\"rapidViewId\":rapid_view_id,\"mappedColumns\":[{\"mappedStatuses\":[{\"id\":\"1\"}],\"id\":59,\"name\":\"Open\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10012\"},{\"id\":\"10010\"}],\"id\":837,\"name\":\"In Development\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10015\"},{\"id\":\"10014\"},{\"id\":\"10017\"}],\"id\":91,\"name\":\"To verify/release\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10024\"},{\"id\":\"10001\"},{\"id\":\"10016\"}],\"id\":61,\"name\":\"Done\",\"isKanPlanColumn\":false}]}",
            'MKT': "{\"currentStatisticsField\":{\"id\":\"none_\"},\"rapidViewId\":rapid_view_id,\"mappedColumns\":[{\"mappedStatuses\":[{\"id\":\"1\"}],\"id\":1658,\"name\":\"To Do\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10030\"},{\"id\":\"10045\"},{\"id\":\"10054\"},{\"id\":\"10049\"},{\"id\":\"10041\"},{\"id\":\"10029\"},{\"id\":\"10066\"},{\"id\":\"10056\"},{\"id\":\"10081\"},{\"id\":\"10059\"},{\"id\":\"10058\"},{\"id\":\"10048\"},{\"id\":\"10042\"},{\"id\":\"10050\"},{\"id\":\"10044\"},{\"id\":\"10046\"},{\"id\":\"10052\"},{\"id\":\"10020\"},{\"id\":\"10065\"},{\"id\":\"10055\"},{\"id\":\"10079\"},{\"id\":\"10063\"},{\"id\":\"10062\"},{\"id\":\"10078\"},{\"id\":\"10061\"},{\"id\":\"10060\"},{\"id\":\"10057\"},{\"id\":\"10043\"},{\"id\":\"10051\"},{\"id\":\"10080\"},{\"id\":\"10040\"},{\"id\":\"10047\"},{\"id\":\"10067\"},{\"id\":\"10082\"},{\"id\":\"10064\"},{\"id\":\"10085\"},{\"id\":\"10083\"},{\"id\":\"10084\"},{\"id\":\"10075\"},{\"id\":\"10021\"},{\"id\":\"10077\"}],\"id\":1659,\"name\":\"In Progress\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10016\"},{\"id\":\"10001\"}],\"id\":1660,\"name\":\"Done\",\"isKanPlanColumn\":false}]}",
            'DSG': "{\"currentStatisticsField\":{\"id\":\"none_\"},\"rapidViewId\":rapid_view_id,\"mappedColumns\":[{\"mappedStatuses\":[{\"id\":\"1\"}],\"id\":1365,\"name\":\"To Do\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10069\"},{\"id\":\"10012\"},{\"id\":\"10068\"},{\"id\":\"10072\"},{\"id\":\"10070\"},{\"id\":\"10071\"},{\"id\":\"10073\"}],\"id\":1366,\"name\":\"In Progress\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10020\"}],\"id\":1662,\"name\":\"Review Failed\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10021\"},{\"id\":\"10074\"}],\"id\":1676,\"name\":\"Sent to Client\",\"isKanPlanColumn\":false},{\"mappedStatuses\":[{\"id\":\"10001\"}],\"id\":1367,\"name\":\"Done\",\"isKanPlanColumn\":false}]}"
        }
        return switcher.get(boardType, "")

    # Get currently set issue types from project
    # cookie - for authorization
    # projectCode - the code of jira project
    def __getIssueTypes__(self, cookie, projectCode):
        try:
            # Prepare url and headers
            url = 'https://cognitivecreators.atlassian.net/rest/api/2/project/' + projectCode
            headers = {'Content-Type': 'application/json', 'Cookie': cookie}

            # Create request
            r = requests.get(url, headers=headers)
            
            # Get issue type ids and return them
            responseDict = json.loads(r.text)
            issueTypes = []
            for issueType in responseDict['issueTypes']:
                issueTypes.append(issueType['id'])
        except:
            raise Exception('Error while getting issue types')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Error while getting issue types')

        return issueTypes

    # Set issue types for project, adding new issue tpyes for new board to be added
    # cookie - for authorization
    # projectId - the id of jira project
    # projectCode - the code of jira project
    # boardType - type of board
    # issueTypes - currently selected issue types on project
    def __setupIssueTypes__(self, cookie, projectId, projectCode, boardType, issueTypes):
        try:
            # Prepare url, json_data and headers
            url = 'https://cognitivecreators.atlassian.net/secure/admin/ConfigureOptionSchemes.jspa?' + self.__getUrlPathForSetupIssueTypesCall__(boardType, issueTypes)
            body = self.__getBodyForSetupIssueTypesCall__(cookie, projectId, projectCode)
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie}

            # Create request
            r = requests.post(url, data=body, headers=headers)
        except:
            raise Exception('Error while setting issue types')

        # Check for failed call
        if r.status_code >= 400:
            raise Exception('Error while setting issue types')

        return r.text

    # Create url path with selected issue types for setup issue types call based on board type
    # boardType - type of board
    # issueTypes - currently selected issue types on project
    def __getUrlPathForSetupIssueTypesCall__(self, boardType, issueTypes):
        self.__addIssueTypesByBoardType__(boardType, issueTypes)
        path = ''
        for issueType in issueTypes:
            path += 'selectedOptions=' + issueType + '&'

        path = path[:-1]
        return path

    # Append issue types based on board id to currently selected issue types
    # boardType - type of board
    # issueTypes - currently selected issue types on project
    def __addIssueTypesByBoardType__(self, boardType, issueTypes):
        if boardType == 'PO':
            issueTypes.extend(['10009', '10010'])
        elif boardType == 'DEV':
            issueTypes.extend(['10004', '10018', '10017', '10016', '10015'])
        elif boardType == 'MKT':
            issueTypes.extend(['10019', '10020'])
        elif boardType == 'DSG':
            issueTypes.extend(['10013', '10014'])
         
        # Remove dublicates if there are any
        issueTypes = list(dict.fromkeys(issueTypes))
        return issueTypes

    # Define body for setup issue types call based on projectCode
    # cookie - for authorization
    # projectId - the id of jira project
    # projectCode - the code of jira project
    def __getBodyForSetupIssueTypesCall__(self, cookie, projectId, projectCode):
        schemeDict = self.__getIssueTypeSchemeIdAndName__(cookie, projectCode)
        bodyDict = {'schemeId': schemeDict['id'], 'projectId': projectId, 'name': schemeDict['name'], 'atl_token': self.__getAtlTokenFromCookie__(cookie), 'defaultOption': ''}
        
        return bodyDict

    # Get project issue type scheme id and name and return as a dictionary {'id': id, 'name': name}
    # cookie - for authorization
    # projectCode - the code of jira project
    def __getIssueTypeSchemeIdAndName__(self, cookie, projectCode):
         # Prepare url and headers
        url = 'https://cognitivecreators.atlassian.net/plugins/servlet/project-config/' + projectCode + '/issuetypes'
        headers = {'Content-Type': 'application/json', 'Cookie': cookie}

        # Create request
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')

        issueTypeSchemeId = soup.findAll("a", {"id": "project-config-issuetype-scheme-edit"})[0].get('data-id')
        issueTypeSchemeName = soup.findAll("span", {"class": "project-config-scheme-name"})[0].string

        return {'id': issueTypeSchemeId, 'name': issueTypeSchemeName}

    # Get atl_token from cookie
    # cookie - contains atl_token which is returned by function
    def __getAtlTokenFromCookie__(self, cookie):
        atl_token_key = 'atlassian.xsrf.token='
        return cookie[int(cookie.find(atl_token_key) + len(atl_token_key)):int(len(cookie))]

    # Add worklow with related issue types call - we will call two separate calls from this - a post call to create draft, a put call to update draft values
    # Returns newly added workflow scheme id as string
    # cookie - for authorization
    # projectCode - the code of jira project
    # boardType - type of board
    # issueTypes - issue types array with issue types to assign to workflow
    def __addWorkflowWithIssueTypes__(self, cookie, projectCode, boardType, issueTypes):
        try:
            self.__addWorkflowWithIssueTypesPostCall__(cookie, projectCode)
            response = self.__addWorkflowWithIssueTypesPutCall__(cookie, projectCode, boardType, issueTypes)
            return str(json.loads(response.text)['id'])
        except:
            raise Exception('Error while adding workflow with issue types')

    # Add worklow with related issue types call - post call to create draft
    # cookie - for authorization
    # projectCode - the code of jira project
    def __addWorkflowWithIssueTypesPostCall__(self, cookie, projectCode):
         # Prepare url, body and headers
        url = 'https://cognitivecreators.atlassian.net/rest/projectconfig/latest/workflowscheme/' + projectCode
        body = '{"draftScheme": false}'
        headers = {'Content-Type': 'application/json', 'Cookie': cookie}

        # Create request
        response = requests.post(url, json=body, headers=headers)

        # Check for failed call
        if response.status_code >= 400:
            raise Exception('Error while adding workflow with issue types - post call')

        return response

    # Add worklow with related issue types call - put call to update values
    # cookie - for authorization
    # projectCode - the code of jira project
    # boardType - type of board
    # issueTypes - issue types array with issue types to assign to workflow
    def __addWorkflowWithIssueTypesPutCall__(self, cookie, projectCode, boardType, issueTypes):
         # Prepare url, body and headers
        url = 'https://cognitivecreators.atlassian.net/rest/projectconfig/latest/draftworkflowscheme/' + projectCode
        body = json.dumps(self.__getBodyForAddWorkflowWithIssueTypesCall__(boardType, issueTypes))
        headers = {'Content-Type': 'application/json', 'Cookie': cookie}

        # Create request
        response = requests.put(url, data=body, headers=headers)

        # Check for failed call
        if response.status_code >= 400:
            raise Exception('Error while adding workflow with issue types - put call')
        return response

    # Define body for add worklow with issue types put call
    # boardType - type of board
    # issueTypes - issue types array with issue types to assign to workflow
    def __getBodyForAddWorkflowWithIssueTypesCall__(self, boardType, issueTypes):
        workflowName = self.__getWorkflowNameByBoardType__(boardType)
        bodyDict = {"name":workflowName,"displayName":workflowName,"issueTypes":issueTypes,"default":True,"description":"","system":False}
        
        return bodyDict

    # Get workflow name by boardType
    # boardType - type of board
    def __getWorkflowNameByBoardType__(self, boardType):
        switcher = {
            'PO': 'Project organizational workflow',
            'DEV': 'Scrum Development Workflow',
            'MKT': 'Marketing Workflow',
            'DSG': 'Design Workflow',
        }
        return switcher.get(boardType, "")

    # Publish newly added workflow scheme
    # cookie - for authorization
    def __publishWorkflowScheme__(self, cookie, projectId, workflowSchemeId):
        try:
            # Prepare url, body and headers
            url = 'https://cognitivecreators.atlassian.net/secure/project/SelectProjectWorkflowSchemeStep2.jspa'
            body = self.__getBodyForPublishWorkflowSchemeCall__(cookie, projectId, workflowSchemeId)
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie}

            # Create request
            response = requests.post(url, data=body, headers=headers)
        except:
            raise Exception('Error while publishing workflow scheme')

        # Check for failed call
        if response.status_code >= 400:
            raise Exception('Error while publishing workflow scheme')
        
        return response

    # Define body for publish workflow scheme call
    # cookie - for authorization
    # projectId - the id of jira project
    # schemeId - the id of workflow scheme
    def __getBodyForPublishWorkflowSchemeCall__(self, cookie, projectId, schemeId):
        bodyDict = {'projectId': projectId, 'schemeId': schemeId, 'draftMigration': True, 'projectIdsParameter': projectId, 'atl_token': self.__getAtlTokenFromCookie__(cookie), 'Associate': 'Associate'}
        return bodyDict

    ################ End of Private methods ################
