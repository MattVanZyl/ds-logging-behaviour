from itertools import combinations
from typing import List
import csv
import pandas as pd
import numpy as np

def export_summary(config, repo_details, log_count, log_levels, log_vs_nonlog):
    final_list = []
    cnt = 0

    for repo, repodata in log_levels.items():
        # To add the all the repo related data in the before hand
        final_list.append([repo_details[repo]['type'], repo, repo_details[repo]['repo_link']])
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

    with open(f"{config['output_path']}log_metrics_summarized.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Repo Type', 'Repo Name', 'Repo Link', 'Number of Lines', 'Logging', 'Trace-Traceback', 'Stderr', 'Print',
             'io-file.write', "DataScience Changes/Total Changes", "Actual Changed Log lines", "Files Count",
             'Total Classes', 'Total Method', 'Total Debug type', 'Total Info Type', 'Total Warning Type',
             'Total Error Type', 'Total Fatal type', 'Total Trace type', "Actual Log Lines"])
        writer.writerows(final_list)

def export_final(config, repo_details, log_counts, log_levels, log_vs_nonlog):
    final_list = []
    cnt = 0

    for repo_name, level_data in log_levels.items():
        # Log Level
        for file_, log_data in level_data.items():
            final_list.append([repo_details[repo_name]['type'], repo_name, repo_details[repo_name]['repo_link'],log_counts[repo_name]['logging'],log_counts[repo_name]['trace-traceback'], log_counts[repo_name]['stderr'], log_counts[repo_name]['print'],log_counts[repo_name]['io-file.write']])

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

            final_list[cnt].extend(
                [file_, log_data['end_line_']['line'], log_den_file, log_den_class, log_den_method,
                 log_count_sep['info'], log_count_sep['error'], log_count_sep['warning'],
                 log_count_sep['debug'], log_count_sep['trace'], log_count_sep['fatal'],
                 log_count_sep_class['info'], log_count_sep_class['error'], log_count_sep_class['warning'],
                 log_count_sep_class['debug'], log_count_sep_class['trace'], log_count_sep_class['fatal'],
                 log_count_sep_method['info'], log_count_sep_method['error'], log_count_sep_method['warning'],
                 log_count_sep_method['debug'], log_count_sep_method['trace'], log_count_sep_method['fatal']])

            final_list[cnt].extend([log_vs_nonlog[repo_name]['logchanges'], log_vs_nonlog[repo_name]['nonlogchanges']])

            cnt += 1

    with open(f"{config['output_path']}final.csv", 'w', newline='') as file:
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

def export_gini(config):
    def gini(x: List[float]) -> float:
        x = np.array(x, dtype=np.float32)
        n = len(x)
        diffs = sum(abs(i - j) for i, j in combinations(x, r=2))
        return diffs / (n ** 2 * x.mean())

    log_metrics_data = pd.read_csv(f"{config['output_path']}final.csv")
    final_list = []
    repo_list = ['Type of Repo', 'Repo Name', 'Repo GiniIndex', 'File GiniIndex', 'Class GiniIndex', 'Method GiniIndex',
                 'File GiniIndex Info', 'File GiniIndex Error', 'File GiniIndex Warning', 'File GiniIndex Debug',
                 'File GiniIndex Trace', 'File GiniIndex Fatal', 'Class GiniIndex Info', 'Class GiniIndex Error',
                 'Class GiniIndex Warning', 'Class GiniIndex Debug', 'Class GiniIndex Trace', 'Class GiniIndex Fatal',
                 'Method GiniIndex Info', 'Method GiniIndex Error', 'Method GiniIndex Warning',
                 'Method GiniIndex Debug', 'Method GiniIndex Trace', 'Method GiniIndex Fatal']
    # print(log_metrics_data.head(20))
    for row in range(0, log_metrics_data.shape[0]):
        if log_metrics_data.iloc[row, 0] in ['data_science', 'non_data_science']:
            # print(repo_list)
            final_list.append(repo_list)
            gini_list = []
            for _ in range(21):
                gini_list.append([])
            repo_list = [log_metrics_data.iloc[row, 0], log_metrics_data.iloc[row, 1]]
            gini_repo = gini([log_metrics_data.iloc[row, index] for index in range(3, 8)])
            repo_list.append(gini_repo)
        else:
            if row != log_metrics_data.shape[0] - 1:
                if log_metrics_data.iloc[row + 1, 0] not in ['data_science', 'non_data_science']:
                    for col in range(10, 31):
                        gini_list[col - 10].append(log_metrics_data.iloc[row, col])
                else:
                    gini_sep_ = []
                    for col in range(0, 21):
                        gini_sep_.append(gini(gini_list[col]))
                    repo_list.extend(gini_sep_)
            else:
                for col in range(10, 31):
                    gini_list[col - 10].append(log_metrics_data.iloc[row, col])
                gini_sep_ = []
                for col in range(0, 21):
                    gini_sep_.append(gini(gini_list[col]))
                repo_list.extend(gini_sep_)
                final_list.append(repo_list)

    # For writing all the gini index values to gini_index.csv
    with open(f"{config['output_path']}gini_index.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(final_list)
