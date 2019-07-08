from rest_framework.decorators import api_view
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from jiraNOApi.service import Service

from .models import Board

import requests
import json


@api_view(["POST"])
def index(request):
    try:
        # Create dictionary from request body
        json_data = json.loads(request.body)

        # Get cookie from header
        cookie = request.META.get('HTTP_X_JIRA_COOKIE')

        # Instantiate service class
        service = Service()

        # Get project id based on project code and add to json_data
        projectId = service.getProjectId(cookie, service.getProjectCodeFromName(json_data['name']))
        json_data['projectIds'] = [projectId]
        json_data['locationId'] = projectId

        # Setup issue types and workflow
        response = service.setupIssueTypesAndWorkflow(cookie, json_data['projectIds'][0], service.getProjectCodeFromName(json_data['name']), service.getBoardTypeFromName(json_data['name']))

        # Create board
        responseText = service.createBoard(cookie, json_data)
        responseDict = json.loads(responseText)
        board = Board.create(responseDict['id'], responseDict['name'])

        # Setup query filter
        service.setupFilterQuery(cookie, service.getProjectCodeFromName(board.board_name), str(board.board_id), service.getBoardTypeFromName(board.board_name))

        # Setup columns
        service.setupColumns(cookie, service.getBoardTypeFromName(board.board_name), str(board.board_id))
    except Exception as error:
        error_dict = {'error': error.args[0]}
        return Response(json.dumps(error_dict), status=HTTP_400_BAD_REQUEST)

    # Return response
    return Response(board.toJSON(), status=HTTP_200_OK)
    