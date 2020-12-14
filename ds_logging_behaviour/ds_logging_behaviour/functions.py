from .fields import LinkFields
import json
import csv

def initialise(repo_data):
    api_links = repo_data[LinkFields.API_LINK]
    repo_links = repo_data[LinkFields.REPO_LINK]
    types = repo_data[LinkFields.TYPE]
    return api_links, repo_links, types

def save_json(dictionary, fname = 'output.json'):
    with open(fname, "w") as output:
        json.dump(dictionary, output)

def read_json(fname):
    with open(fname) as f:
        data = json.load(f)
    return data


def export_summary(config, repo_details, log_count, log_levels, log_vs_nonlog):
    final_list = []
    cnt = 0

    for repo, repodata in log_levels.items():
        # To add the all the repo related data in the before hand
        final_list.append([repo_details[repo]['Type'], repo, repo_details[repo]['Repo Link']])
        total = {'class_': 0, 'method_': 0, 'end_line_': 0, 'info': 0, 'error': 0, 'warning': 0, 'debug': 0, 'trace': 0,
                 'fatal': 0}
        files_count = 0
        log_level_lines = ""
        for file_, log_data in repodata.items():
            files_count += 1
            for log_name, log_level in log_data.items():
                if log_name == "end_line_":
                    total["end_line_"] += log_data['end_line_']["line"]
                elif log_name in total.keys():
                    total[log_name] += log_data[log_name]["count"]
                if log_name in ['info', 'error', 'warning', 'debug', 'trace', 'fatal']:
                    log_level_lines += log_data['logs'] + ','

        total_log_lines = log_vs_nonlog[repo]['log_lines']
        if total_log_lines == []:
            total_log_lines = 'No logs'
        else:
            total_log_lines = ""
            for log_line in log_vs_nonlog[repo]['log_lines']:
                total_log_lines += log_line

        final_list[cnt].extend(
            [total['end_line_'], log_count[repo]['logging'], log_count[repo]['trace-traceback'], log_count[repo]['stderr'],
             log_count[repo]['print'], log_count[repo]['io-file.write'],
             f"{log_vs_nonlog[repo]['logchanges']} / {log_vs_nonlog[repo]['logchanges'] + log_vs_nonlog[repo]['nonlogchanges']}",
             total_log_lines, files_count, total['class_'], total['method_'], total['debug'], total['info'],
             total['warning'], total['error'], total['fatal'], total['trace'], log_level_lines])
        cnt += 1

    # For adding all the data to the LogMetrics-Summarized.csv
    with open(f"{config['output_folder']}LogMetrics-Summarized.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Repo Type', 'Repo Name', 'Repo Link', 'Number of Lines', 'Logging', 'Trace-Traceback', 'Stderr', 'Print',
             'io-file.write', "DataScience Changes/Total Changes", "Actual Changed Log lines", "Files Count",
             'Total Classes', 'Total Method', 'Total Debug type', 'Total Info Type', 'Total Warning Type',
             'Total Error Type', 'Total Fatal type', 'Total Trace type', "Actual Log Lines"])
        writer.writerows(final_list)

def finalcalc(config, repo_details, log_counts, log_levels, log_vs_nonlog):
    final_list = []
    cnt = 0

    for repo_name, level_data in log_levels.items():
        # To add the all the repo related data in the before hand
        final_list.append([repo_details[repo_name]['Type'], repo_name, repo_details[repo_name]['Repo Link'], log_counts[repo_name]['logging'],
                           log_counts[repo_name]['trace-traceback'], log_counts[repo_name]['stderr'], log_counts[repo_name]['print'],
                           log_counts[repo_name]['io-file.write']])
        final_list[cnt].extend(["-"] * 23)
        final_list[cnt].extend([log_vs_nonlog[repo_name]['logchanges'], log_vs_nonlog[repo_name]['nonlogchanges']])
        cnt += 1
        # flag_r = 0
        # Log Level
        for file_, log_data in level_data.items():
            class_counts = {}
            method_counts = {}
            total_classes, total_methods = 0, 0
            log_count = 0
            log_count_sep = {'info': 0, 'error': 0, 'warning': 0, 'debug': 0, 'trace': 0, 'fatal': 0}
            log_count_sep_class = {'info': 0, 'error': 0, 'warning': 0, 'debug': 0, 'trace': 0, 'fatal': 0}
            log_count_sep_method = {'info': 0, 'error': 0, 'warning': 0, 'debug': 0, 'trace': 0, 'fatal': 0}

            for log_name, log_level in log_data.items():
                if log_name in ['info', 'error', 'warning', 'debug', 'trace', 'fatal']:
                    log_count += log_data[log_name]['count']
                    log_count_sep[log_name] += log_data[log_name]['count']
                    for k in log_data[log_name]['lines']:
                        if 'class_' in log_data.keys():
                            for c in log_data['class_']['lines']:
                                if k[0] > c[0] and k[0] < c[1]:
                                    class_name = 'class_' + str(c[0]) + "-" + str(c[1])
                                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                                    log_count_sep_class[log_name] += 1
                        if 'method_' in log_data.keys():
                            for m in log_data['method_']['lines']:
                                if k[0] > m[0] and k[0] < m[1]:
                                    method_name = 'method_' + str(m[0]) + "-" + str(m[1])
                                    method_counts[method_name] = method_counts.get(method_name, 0) + 1
                                    log_count_sep_method[log_name] += 1
                else:
                    if log_name == 'class_':
                        total_classes += log_data['class_']['count']
                    elif log_name == 'method_':
                        total_methods += log_data['method_']['count']

            # Log Density
            log_den_file, log_den_class, log_den_method = 0, 0, 0
            numof_lines = log_data['end_line_']['line']
            if numof_lines != 0:
                log_den_file = log_count / numof_lines
            if 'class_' in log_data.keys() and total_classes != 0:
                log_den_class = log_count / total_classes
            if 'method_' in log_data.keys() and total_methods != 0:
                log_den_method = log_count / total_methods
            # if flag_r == 1:
            final_list.append([""] * 8)
            final_list[cnt].extend(
                [file_, log_data['end_line_']['line'], log_den_file, log_den_class, log_den_method,
                 log_count_sep['info'], log_count_sep['error'], log_count_sep['warning'],
                 log_count_sep['debug'], log_count_sep['trace'], log_count_sep['fatal'],
                 log_count_sep_class['info'], log_count_sep_class['error'], log_count_sep_class['warning'],
                 log_count_sep_class['debug'], log_count_sep_class['trace'], log_count_sep_class['fatal'],
                 log_count_sep_method['info'], log_count_sep_method['error'], log_count_sep_method['warning'],
                 log_count_sep_method['debug'], log_count_sep_method['trace'], log_count_sep_method['fatal'],
                 "", ""])
            '''if flag_r == 0:
                final_list[cnt].extend(["-"] * 23)
                final_list[cnt].extend([logvsnlog[repo]['logchanges'] , logvsnlog[repo]['nonlogchanges']])'''

            # flag_r = 1
            cnt += 1

        '''if flag_r == 0:
            final_list[cnt].extend(["-"] * 23)'''


    # For adding all the data to the FINAL.csv
    with open(f"{config['output_folder']}FINAL.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['DataScience/NonDataScience', 'Repo Name', 'Repo Link', 'Instances of Log - Logger',
                         'Instances of Log - Trace/Traceback', 'Instances of Log -StdErr',
                         'Instances of Log - Print', 'Instances of Log - IO/File.write', 'FileName',
                         'Log Density - Lines', 'Log Density - File', 'Log Density - Class',
                         'Log Density - Method', 'Log Level File - Info', 'Log Level File - Error',
                         'Log Level File - Warning', 'Log Level File - Debug', 'Log Level File - Trace',
                         'Log Level File - Fatal', 'Log Level Class - Info', 'Log Level Class - Error',
                         'Log Level Class - Warning', 'Log Level Class - Debug', 'Log Level Class - Trace',
                         'Log Level Class - Fatal', 'Log Level Method - Info', 'Log Level Method - Error',
                         'Log Level Method - Warning', 'Log Level Method - Debug', 'Log Level Method - Trace',
                         'Log Level Method - Fatal', 'DataScience Related Changes',
                         'Non DataScience Related Changes'])
        writer.writerows(final_list)
