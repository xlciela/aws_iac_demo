import boto3
import csv

client = boto3.client('cloudwatch', region_name='ap-northeast-1')

if __name__ == "__main__":
    response = client.describe_alarms(
        AlarmTypes=[
            'CompositeAlarm',
            'MetricAlarm'
        ],
        MaxRecords=100
    )

    with open('Alarm.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')

        KEY_LIST = [
            'AlarmName',
            'AlarmDescription',
            'ActionEnabled',
            'StateValue',
            'AlarmActions',
            'InsufficientDataActions',
            'MetricName',
            'Namespace',
            'Statistic',
            'Dimensions',
            'Period',
            'EvaluationPeriods',
            'DatapointsToAlarm',
            'Threshold',
            'ComparisonOperator',
            'TreatMissingData',
        ]
        writer.writerow(['sep=', ''])
        writer.writerow(KEY_LIST)
        while True:
            for alarm in response['MetricAlarms']:
                value = []
                for key in KEY_LIST:
                    try:
                        value.append(alarm.get(key, ''))
                    except Exception as e:
                        value.append(f"E: {e}")

                writer.writerow(value)
            
            # print(response)
            if response.get('NextToken') is None:
                break
            response = client.describe_alarms(
                AlarmTypes=[
                    'CompositeAlarm',
                    'MetricAlarm'
                ],
                MaxRecords=100,
                NextToken=response['NextToken']
            )
                