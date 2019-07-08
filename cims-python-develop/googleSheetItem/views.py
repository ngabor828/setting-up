import httplib2
import os

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)
from rest_framework.response import Response
from apiclient import discovery
from google.oauth2 import service_account
from .models import GoogleSheetItem

import json


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def index(request):
    # Get row number
    json_data = json.loads(request.body)
    row = json_data['row']

    # Get data in row
    try:
        # Authorize service account
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        secret_file = os.path.join(os.getcwd(), 'googleSheetItem/client_secret.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)

        # TODO: change this to real spreadsheet id
        spreadsheet_id = '1ABW6fYaKeCDTolFlCVbDvaFPyQeT7LvBHuXj1dJoQMk'

        # Create range by row
        range_name= 'Sheet1!A' + row + ':P' + row

        # Get data from spreadsheet
        data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        if 'values' not in data:
            return Response("No values sent", status=HTTP_400_BAD_REQUEST)
        attribute_list = data['values'][0]
        
        # Get GoogleSheetItem by attributeList
        googleSheetItem = GoogleSheetItem.create(row, attribute_list)

        # Check if item was saved to database
        if googleSheetItem is not None:
            return Response("Response", status=HTTP_200_OK)
        else:
            return Response("No object created", status=HTTP_400_BAD_REQUEST)

    except OSError as error:
        return Response(error, status=HTTP_200_OK)
