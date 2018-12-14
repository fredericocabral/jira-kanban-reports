from jira import JIRA
from dateutil.parser import parse
from termcolor import colored, cprint


class Reporter:

    def merge_qas(self, data):
        qa = 0
        for key, value in data.items():
            if 'QA' in key:
                qa += data[key]

        data['QA'] = qa
        del data['In QA']
        del data['QA failed']
        del data['Needs QA']

        return data

    def merge_in_development_with_in_progress(self, data):
        in_development = data['In Development']
        in_progress = data['In Progress']
        data['In Development'] = in_development + in_progress
        del data['In Progress']
        return data


    def render(self, data):

        # merge QA's columns
        # data = self.merge_qas(data)
        data = self.merge_in_development_with_in_progress(data)
    
        for key, value in data.items():
            bar = ''
            for i in range(int(value)):
                bar += '|'
                cycle_time = value/total_tickets
            bar = colored(bar, 'green')
            print("%-25s %-10s " % (f'{key}', f'[{bar}] {str(value)} %'))
        return 1


jira = JIRA(
    server='https://jira.deliveryhero.com',
    basic_auth=('frederico.cabral', 'eTnp0as3')
)


statuses = {}
i = 0

total_tickets = 20

#issues = jira.search_issues('project=LOGT AND issuetype=Story AND component in ("Roadrunner iOS", "Roadrunner Android") AND status=Closed order by Created  desc', maxResults=total_tickets)
issues = jira.search_issues('project = LOGT AND issuetype = Story  AND component in ("Roadrunner Android", "Roadrunner iOS") AND status changed FROM "Ready For Production" to "Closed" order by updated desc', maxResults=total_tickets)

for issue in issues:

    issue = jira.issue(issue.key, expand='changelog')

    previous = parse(issue.fields.created)
    last_item = None

    for idx, history in enumerate(issue.changelog.histories):
        for item in history.items:
            if item.field == 'status':
                current = parse(history.created)
                spent = (current - previous).days

                if item.fromString in statuses:
                    statuses[item.fromString] += spent
                else:
                    statuses[item.fromString] = spent

                last_item = item.fromString
                previous = parse(history.created)
                i = i + 1


if 'In Review' in statuses:
    del statuses['In Review']

total = sum(statuses.values())

percentual = {}

for k, v in statuses.items():
    percent = (v * 100 / total)
    percentual[k] = round(percent, 2)

print(percentual)

Reporter().render(percentual)

lead_time = total/total_tickets
lead_time_report = colored(f'{lead_time} days', 'yellow')

print(f'\n\nLead Time: {lead_time_report}')


print('\n\n\n------------\n\n\n')


# remove backlog
del statuses['Backlog']
del statuses['Ready for Development']
del statuses['In Refinement']

total = sum(statuses.values())

percentual = {}
for k, v in statuses.items():
    percent = (v * 100 / total)
    percentual[k] = round(percent, 2)

print(percentual)

Reporter().render(percentual)

lead_time = total/total_tickets
lead_time_report = colored(f'{lead_time} days', 'yellow')

print(f'\n\nImplementation Time: {lead_time_report}')
