from django.db import models
from enum import Enum
import datetime
from django.utils.timezone import make_aware


class Values(Enum):  
    TIMESTAMP = 0
    EMAIL = 1
    INPUT_REASON = 2
    DATE = 3
    NUMBER_OF_EXTRA_HOURS = 4
    SHORT_SUMMARY = 5
    COMPENSATION_TYPE = 6
    TYPE_OF_EXPENSES = 7
    START_DATE = 8
    END_DATE = 9
    SUMMARY_OF_COSTS = 10
    AMOUNT_OF_EXPENSES_IN_RON = 11
    YEAR = 12
    MONTH = 13
    APPROVED_HOURS_OR_EXPENSES = 14
    APPROVAL = 15


class GoogleSheetItem(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField('Timestamp', blank=True, null=True)
    email_address = models.CharField(max_length=100)
    input_reason = models.CharField(max_length=100)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    approved_hours_or_expenses = models.FloatField(blank=True, null=True)
    approval = models.CharField(max_length=100)

    @classmethod
    def create(cls, id, attribute_list):
        print('ROW: ' + id)
        # for x in range(lenist[x]) 
        if attribute_list[2] == 'Extra costs':
            print('Extra cost')
            return ExtraCost.create(id, attribute_list)
        elif attribute_list[2] == 'Overtime':
            print('Overtime')
            return Overtime.create(id, attribute_list)
        return GoogleSheetItem.objects.update_or_create(id=id, defaults={
                                                            'email_address': attribute_list[Values.EMAIL.value],
                                                            'timestamp': make_aware(datetime.datetime.strptime(attribute_list[Values.TIMESTAMP.value], '%m/%d/%Y %H:%M:%S')),
                                                            'input_reason': attribute_list[Values.INPUT_REASON.value],
                                                            'year': None if attribute_list[Values.YEAR.value] is '' else attribute_list[Values.YEAR.value],
                                                            'month': None if attribute_list[Values.MONTH.value] is '' else attribute_list[Values.MONTH.value],
                                                            'approved_hours_or_expenses': None if attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value] is '' else attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value],
                                                            'approval': attribute_list[Values.APPROVAL.value],
                                                        })


class ExtraCost(GoogleSheetItem):
    type_of_expenses = models.CharField(max_length=100)
    start_date = models.DateTimeField('Start date', blank=True, null=True)
    end_date = models.DateTimeField('End date', blank=True, null=True)
    summary_of_costs = models.CharField(max_length=200)
    amount_of_expenses_in_RON = models.FloatField(default=0)

    @classmethod
    def create(cls, id, attribute_list):
        return ExtraCost.objects.update_or_create(id=id, defaults={
                                                            'email_address': attribute_list[Values.EMAIL.value],
                                                            'timestamp': make_aware(datetime.datetime.strptime(attribute_list[Values.TIMESTAMP.value], '%m/%d/%Y %H:%M:%S')),
                                                            'input_reason': attribute_list[Values.INPUT_REASON.value],
                                                            'year': None if attribute_list[Values.YEAR.value] is '' else attribute_list[Values.YEAR.value],
                                                            'month': None if attribute_list[Values.MONTH.value] is '' else attribute_list[Values.MONTH.value],
                                                            'approved_hours_or_expenses': None if attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value] is '' else attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value],
                                                            'approval': attribute_list[Values.APPROVAL.value],
                                                            'type_of_expenses': attribute_list[Values.TYPE_OF_EXPENSES.value],
                                                            'start_date': make_aware(datetime.datetime.strptime(attribute_list[Values.START_DATE.value], '%m/%d/%Y')),
                                                            'end_date': make_aware(datetime.datetime.strptime(attribute_list[Values.END_DATE.value], '%m/%d/%Y')),
                                                            'summary_of_costs': attribute_list[Values.SUMMARY_OF_COSTS.value],
                                                            'amount_of_expenses_in_RON': None if attribute_list[Values.AMOUNT_OF_EXPENSES_IN_RON.value] is '' else attribute_list[Values.AMOUNT_OF_EXPENSES_IN_RON.value],
                                                        })


class Overtime(GoogleSheetItem):
    date = models.DateTimeField('Date', blank=True, null=True)
    number_of_extra_hours = models.IntegerField(default=0)
    short_summary = models.CharField(max_length=500)
    compensation_type = models.CharField(max_length=100)

    @classmethod
    def create(cls, id, attribute_list):
        return Overtime.objects.update_or_create(id=id, defaults={
                                                            'email_address': attribute_list[Values.EMAIL.value],
                                                            'timestamp': make_aware(datetime.datetime.strptime(attribute_list[Values.TIMESTAMP.value], '%m/%d/%Y %H:%M:%S')),
                                                            'input_reason': attribute_list[Values.INPUT_REASON.value],
                                                            'year': None if attribute_list[Values.YEAR.value] is '' else attribute_list[Values.YEAR.value],
                                                            'month': None if attribute_list[Values.MONTH.value] is '' else attribute_list[Values.MONTH.value],
                                                            'approved_hours_or_expenses': None if attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value] is '' else attribute_list[Values.APPROVED_HOURS_OR_EXPENSES.value],
                                                            'approval': attribute_list[Values.APPROVAL.value],
                                                            'date': make_aware(datetime.datetime.strptime(attribute_list[Values.DATE.value], '%m/%d/%Y')),
                                                            'number_of_extra_hours': None if attribute_list[Values.NUMBER_OF_EXTRA_HOURS.value] is '' else attribute_list[Values.NUMBER_OF_EXTRA_HOURS.value],
                                                            'short_summary': attribute_list[Values.SHORT_SUMMARY.value],
                                                            'compensation_type': attribute_list[Values.COMPENSATION_TYPE.value],
                                                        })
