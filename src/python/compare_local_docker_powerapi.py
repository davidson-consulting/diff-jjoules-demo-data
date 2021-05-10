import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import datetime
import math
import os

def run_cmd(cmd):
    print(cmd)
    os.system(cmd)

def print_to_file(text, filepath):
    with open(filepath, 'a') as file:
        file.write(str(text) + '\n')

def to_test_name(test):
    return test.split('-')[-1].split('.json')[0]

def create_datetime_from_str(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')

def collect_entries(target, data, threshold=20):
    entries = []
    currentEntries = []
    for d in data:
        if d['target'] == target:
            current_timestamp = d['timestamp']
            current_timestamp_object = create_datetime_from_str(current_timestamp)
            if len(currentEntries) > 0 and ( (current_timestamp_object - currentEntries[-1]['timestamp']).total_seconds() > threshold):
                entries.append(currentEntries)
                currentEntries = []
            else:
                currentEntries.append({
                    'timestamp': current_timestamp_object,
                    'power': d['power'],
                    'target': d['target']
                })
    entries.append(currentEntries)
    return entries

def run_target(target, data, threshold=20):
    powers, energies, durations = [], [], []
    entries = collect_entries(target, data, threshold)
    for entry in entries:
        power = list(map(lambda e: e['power'], entry))
        times = range(1, len(power) + 1)
        energy = np.trapz(power, times)
        if len(entry) == 0:
            print(target)
            return [], [], [], []
        duration = (entry[-1]['timestamp'] - entry[0]['timestamp']).total_seconds()
        durations.append(duration)
        energies.append(energy)
        powers.append(energy / duration)
    return powers, energies, durations, len(entries)

def read_json(path_to_json):
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    return data

def mediane_delta(data_v1, data_v2):
    return mediane(data_v2) - mediane(data_v1)

def quartiles(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        cursor_middle = int(len(data) / 2)
        return mediane(data[:cursor_middle]), mediane(data[cursor_middle:])
    else:
        cursor_end_q1 = int((len(data) / 2) - 1)
        cursor_begin_q3 = int((len(data) / 2) + 1)
        return mediane(data[:cursor_end_q1]), mediane(data[cursor_begin_q3:])

def mediane(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        middle_cursor = int(len(data) / 2)
        return (data[middle_cursor - 1] + data[middle_cursor]) / 2
    else:
        return data[int(len(data)/2)]

def format(to_format):
    return '{:.2f}'.format(to_format)

def format_perc(value):
    return format(value * float(100)) + '%'

def compute_and_format_perc(med, value):
    return format_perc(float(float(value) / float(med)))

def format_med(med, value):
    return format(value) + ' (' + compute_and_format_perc(med, value) + ')'

def stats(data_test):
    med = mediane(data_test)
    q1, q3 = quartiles(data_test)
    mean = sum(data_test) / len(data_test)
    deviations = [ (x - mean) ** 2 for x in data_test ]
    variance = sum(deviations) / len(deviations)
    stddev = math.sqrt(variance)
    cv = (q3 - q1) / (q3 + q1)
    qcd = stddev / mean
    return med, format_med(med, stddev), format_perc(cv), format_perc(qcd)

def do_stats_for_given_measure(key, measure, data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test):
    med, stddev, cv, qcd = stats([d[key] for d in data_per_test])
    mediane_per_test[measure] = med
    stddev_per_test[measure] = stddev
    cv_per_test[measure] = cv
    qcd_per_test[measure] = qcd
    return mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test

def do_all_stats_for_test(data_per_test,mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test):
    mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test = do_stats_for_given_measure('package|uJ', 'Energy', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)
    mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test = do_stats_for_given_measure('instructions', 'Instructions', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)
    return do_stats_for_given_measure('duration|ns', 'Duration', data_per_test, mediane_per_test, stddev_per_test, cv_per_test, qcd_per_test)

def construct_row_markdown(array_values):
    return '| ' + ' | '.join(array_values) + ' |'

tests = [ 
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapEmptyList.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapOneElement.json',
    'fr.davidson.diff_jjoules_demo.InternalListTest-testMapMultipleElement.json'
]

if __name__ == '__main__':

    prefix_folder_output = 'demo-output/'
    prefix_folder_output_spino = 'demo-output-docker-spino-multiple/'

    data_per_test_v1 = {}
    data_per_test_v2 = {}
    data_spino_per_test_v1 = {}
    data_spino_per_test_v2 = {}

    run_cmd(' '.join(['rm', '-f', prefix_folder_output_spino + 'README.md']))

    
    data = read_json(prefix_folder_output_spino + 'data/diff-jjoules-demo.json')
    targets = ['diff-jjoules-demo-v1', 'diff-jjoules-demo-v2']
    powers_per_target, energies_per_target, durations_per_target, nb_run_per_target = {}, {}, {}, {}
    for target in targets:
        powers, energies, durations, nb_run = run_target(target, data)
        if len(powers) == 0:
            continue
        powers_per_target[target] = powers
        energies_per_target[target] = energies
        durations_per_target[target] = durations
        nb_run_per_target[target] = nb_run

    plt.plot([d for d in energies_per_target['diff-jjoules-demo-v1']], '--', color='blue')
    plt.plot([d for d in energies_per_target['diff-jjoules-demo-v2']], '--', color='red')
    mediane_to_plot = mediane([d for d in energies_per_target['diff-jjoules-demo-v1']])
    plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
    mediane_to_plot = mediane([d for d in energies_per_target['diff-jjoules-demo-v2']])
    plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
    plt.legend(['v1', 'v2'])
    plt.savefig(prefix_folder_output_spino + 'pictures/' +  'powerapi_energy.png')
    plt.clf()

    print_to_file('# PowerAPI', prefix_folder_output_spino + 'README.md')

    print_to_file(
        construct_row_markdown(['version', 'med (J)', 'stddev', 'cv', 'qcd']),
        prefix_folder_output_spino + 'README.md'
    )
    print_to_file(
        construct_row_markdown(['---', '---', '---', '---', '---']),
        prefix_folder_output_spino + 'README.md'
    )

    med, stddev, cv, qcd = stats([d for d in energies_per_target['diff-jjoules-demo-v1']])
    med_v1 = med
    print_to_file(
        construct_row_markdown(['PowerAPI v1', 
            str(med), stddev, cv, qcd
        ]),
        prefix_folder_output_spino + 'README.md'
    )

    med, stddev, cv, qcd = stats([d for d in energies_per_target['diff-jjoules-demo-v2']]) 
    print_to_file(
        construct_row_markdown(['PowerAPI v2', 
            str(med), stddev, cv, qcd
        ]),
        prefix_folder_output_spino + 'README.md'
    )
    print_to_file(
        construct_row_markdown(['PowerAPI Delta Energy (J)', 
            str(med - med_v1)
        ]),
        prefix_folder_output_spino + 'README.md'
    )

    print_to_file(
       '\n',
        prefix_folder_output_spino + 'README.md'
    )

    print_to_file(
        '![powerapi_energy](pictures/powerapi_energy.png)', 
        prefix_folder_output_spino + 'README.md'
    )

    for test in tests:
        data_per_test_v1[test] = []
        data_per_test_v2[test] = []
        data_spino_per_test_v1[test] = []
        data_spino_per_test_v2[test] = []
        for i in range(0,100):
            data_per_test_v1[test].append(read_json(prefix_folder_output + '/v1/' + str(i) + '/' + test))
            data_per_test_v2[test].append(read_json(prefix_folder_output + '/v2/' + str(i) + '/' + test))
            for j in range(1, 101):
                data_spino_per_test_v1[test].append(read_json(prefix_folder_output_spino + 'data/' + str(i) + '/v1/' + str(j) + '/' + test))
                data_spino_per_test_v2[test].append(read_json(prefix_folder_output_spino + 'data/' + str(i) + '/v2/' + str(j) + '/' + test))
        
        print_to_file('## ' + to_test_name(test) + '\n',  prefix_folder_output_spino + 'README.md')
        print_to_file(
            construct_row_markdown(['measures', 'med(uJ/#)', 'stddev', 'cv', 'qcd']),
            prefix_folder_output_spino + 'README.md'
        )
        print_to_file(
            construct_row_markdown(['---', '---', '---', '---', '---']),
            prefix_folder_output_spino + 'README.md'
        )

        mediane_l_v1, stddev_l_v1, cv_l_v1, qcd_l_v1 = {}, {}, {}, {}
        do_all_stats_for_test(
            [d for d in data_per_test_v1[test]],
            mediane_l_v1, stddev_l_v1, cv_l_v1, qcd_l_v1
        )
        mediane_l_v2, stddev_l_v2, cv_l_v2, qcd_l_v2 = {}, {}, {}, {}
        do_all_stats_for_test(
            [d for d in data_per_test_v2[test]],
            mediane_l_v2, stddev_l_v2, cv_l_v2, qcd_l_v2
        )

        mediane_d_v1, stddev_d_v1, cv_d_v1, qcd_d_v1 = {}, {}, {}, {}
        do_all_stats_for_test(
            [d for d in data_spino_per_test_v1[test]],
            mediane_d_v1, stddev_d_v1, cv_d_v1, qcd_d_v1
        )
        mediane_d_v2, stddev_d_v2, cv_d_v2, qcd_d_v2 = {}, {}, {}, {}
        do_all_stats_for_test(
            [d for d in data_spino_per_test_v2[test]],
            mediane_d_v2, stddev_d_v2, cv_d_v2, qcd_d_v2
        )

        for measure in ['Energy', 'Instructions']:
            print_to_file(
                construct_row_markdown([measure + ' local v1', 
                str(mediane_l_v1[measure]), str(stddev_l_v1[measure]), str(cv_l_v1[measure]), str(qcd_l_v1[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
            print_to_file(
                construct_row_markdown([measure + ' local v2', 
                str(mediane_l_v2[measure]), str(stddev_l_v2[measure]), str(cv_l_v2[measure]), str(qcd_l_v2[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
            print_to_file(
                construct_row_markdown([measure + ' delta local',
                str(mediane_l_v2[measure] - mediane_l_v1[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
            print_to_file(
                construct_row_markdown([measure + ' docker v1', 
                str(mediane_d_v1[measure]), str(stddev_d_v1[measure]), str(cv_d_v1[measure]), str(qcd_d_v1[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
            print_to_file(
                construct_row_markdown([measure + ' docker v2', 
                str(mediane_d_v2[measure]), str(stddev_d_v2[measure]), str(cv_d_v2[measure]), str(qcd_d_v2[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
            print_to_file(
                construct_row_markdown([measure + ' delta docker',
                str(mediane_d_v2[measure] - mediane_d_v1[measure])]),
                prefix_folder_output_spino + 'README.md'
            )
        
        print_to_file(
            '\n',
            prefix_folder_output_spino + 'README.md'
        )

        '''
        plt.plot([d['package|uJ'] for d in data_per_test_v1[test]], '--', color='blue')
        plt.plot([d['package|uJ'] for d in data_spino_per_test_v1[test]][:100], '--', color='red')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_spino_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
        plt.legend(['E-local', 'E-docker'])
        plt.tight_layout()
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_vs_local_v1_energy.png')
        plt.clf()

        plt.plot([d['instructions'] for d in data_per_test_v1[test]], '--', color='green')
        plt.plot([d['instructions'] for d in data_spino_per_test_v1[test]][:100], '--', color='gold')
        mediane_to_plot = mediane([d['instructions'] for d in data_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='green')
        mediane_to_plot = mediane([d['instructions'] for d in data_spino_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='gold')
        plt.legend(['I-local', 'I-docker'])
        plt.tight_layout()
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_vs_local_v1_instructions.png')
        plt.clf()

        
        print_to_file('### Energy V1 local vs docker\n', prefix_folder_output_spino + 'README.md')
        print_to_file(
            '![docker_vs_local_v1_energy](pictures/' + to_test_name(test) + '_docker_vs_local_v1_energy.png)', 
            prefix_folder_output_spino + 'README.md'
        )
        print_to_file(
            '![docker_vs_local_v1_instructions](pictures/' + to_test_name(test) + '_docker_vs_local_v1_instructions.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )

        plt.plot([d['package|uJ'] for d in data_per_test_v2[test]], '--', color='blue')
        plt.plot([d['package|uJ'] for d in data_spino_per_test_v2[test]][:100], '--', color='red')
        plt.plot([d['instructions'] for d in data_per_test_v2[test]], '--', color='green')
        plt.plot([d['instructions'] for d in data_spino_per_test_v2[test]][:100], '--', color='gold')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_spino_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
        mediane_to_plot = mediane([d['instructions'] for d in data_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='green')
        mediane_to_plot = mediane([d['instructions'] for d in data_spino_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='gold')
        plt.legend(['E-local', 'E-docker', 'I-local', 'I-docker'])
        plt.tight_layout()
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_vs_local_v2_energy.png')
        plt.clf()

        print_to_file('### Energy V2 local vs docker\n', prefix_folder_output_spino + 'README.md')
        print_to_file(
            '![docker_vs_local_v2_energy](pictures/' + to_test_name(test) + '_docker_vs_local_v2_energy.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )
        '''

        plt.plot([d['package|uJ'] for d in data_per_test_v1[test]], '--', color='blue')
        plt.plot([d['package|uJ'] for d in data_per_test_v2[test]], '--', color='red')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
        plt.legend(['E-v1', 'E-v2'])
        plt.tight_layout()
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_local_jjoules_energy.png')
        plt.clf()

        plt.plot([d['instructions'] for d in data_per_test_v1[test]], '--', color='green')
        plt.plot([d['instructions'] for d in data_per_test_v2[test]], '--', color='gold')
        mediane_to_plot = mediane([d['instructions'] for d in data_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='green')
        mediane_to_plot = mediane([d['instructions'] for d in data_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='gold')
        plt.legend(['I-v1', 'I-v2'])
        plt.tight_layout()
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_local_jjoules_instructions.png')
        plt.clf()

        print_to_file('### V1 vs V2 local\n', prefix_folder_output_spino + 'README.md')
        print_to_file(
            '![local_jjoules_energy](pictures/' + to_test_name(test) + '_local_jjoules_energy.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )
        print_to_file(
            '![local_jjoules_energy](pictures/' + to_test_name(test) + '_local_jjoules_instructions.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )
        
        data_spino_per_test_v1_tmp = [d['package|uJ'] for d in data_spino_per_test_v1[test]]
        data_spino_per_test_v2_tmp = [d['package|uJ'] for d in data_spino_per_test_v2[test]]
        data_spino_per_test_v1_tmp_i = [d['instructions'] for d in data_spino_per_test_v1[test]]
        data_spino_per_test_v2_tmp_i = [d['instructions'] for d in data_spino_per_test_v2[test]]

        plt.plot(data_spino_per_test_v1_tmp[0:100], '--', color='blue')
        plt.plot(data_spino_per_test_v2_tmp[0:100], '--', color='red')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_spino_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
        mediane_to_plot = mediane([d['package|uJ'] for d in data_spino_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
        plt.legend(['E-v1', 'E-v2'])
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_jjoules_energy.png')
        plt.clf()

        plt.plot(data_spino_per_test_v1_tmp_i[0:100], '--', color='green')
        plt.plot(data_spino_per_test_v2_tmp_i[0:100], '--', color='gold')
        mediane_to_plot = mediane([d['instructions'] for d in data_spino_per_test_v1[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='green')
        mediane_to_plot = mediane([d['instructions'] for d in data_spino_per_test_v2[test]])
        plt.plot([mediane_to_plot for x in range(0, 100)], color='gold')
        plt.legend(['I-v1', 'I-v2'])
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_jjoules_instructions.png')
        plt.clf()

        print_to_file('### Energy V1 vs V2 docker\n', prefix_folder_output_spino + 'README.md')
        print_to_file(
            '![docker_jjoules_energy](pictures/' + to_test_name(test) + '_docker_jjoules_energy.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )
        print_to_file(
            '![docker_jjoules_energy](pictures/' + to_test_name(test) + '_docker_jjoules_instructions.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )

        print_to_file('### V1 vs V2 docker medianes\n', prefix_folder_output_spino + 'README.md')
        medianes_v1 = []
        medianes_v2 = []
        medianes_v1_i = []
        medianes_v2_i = []
        for i in range(0, 100):
            medianes_v1.append(mediane(data_spino_per_test_v1_tmp[i*100:(i+1)*100]))
            medianes_v2.append(mediane(data_spino_per_test_v2_tmp[i*100:(i+1)*100]))
            medianes_v1_i.append(mediane(data_spino_per_test_v1_tmp_i[i*100:(i+1)*100]))
            medianes_v2_i.append(mediane(data_spino_per_test_v2_tmp_i[i*100:(i+1)*100]))

        plt.plot(medianes_v1, '--', color='blue')
        plt.plot(medianes_v2, '--', color='red')
        mediane_to_plot = mediane(medianes_v1)
        plt.plot([mediane_to_plot for x in range(0, 100)], color='blue')
        mediane_to_plot = mediane(medianes_v2)
        plt.plot([mediane_to_plot for x in range(0, 100)], color='red')
        plt.legend(['E-v1', 'E-v2'])
        plt.savefig(prefix_folder_output_spino + 'pictures/' +  to_test_name(test) + '_docker_jjoules_energy_medianes.png')
        plt.clf()

        plt.plot(medianes_v1_i, '--', color='green')
        plt.plot(medianes_v2_i, '--', color='gold')
        mediane_to_plot = mediane(medianes_v1_i)
        plt.plot([mediane_to_plot for x in range(0, 100)], color='green')
        mediane_to_plot = mediane(medianes_v2_i)
        plt.plot([mediane_to_plot for x in range(0, 100)], color='gold')
        plt.legend(['I-v1', 'I-v2'])
        plt.savefig(prefix_folder_output_spino + 'pictures/' + to_test_name(test) + '_docker_jjoules_instructions_medianes.png')
        plt.clf()

        print_to_file(
            '![docker_jjoules_energy](pictures/' + to_test_name(test) + '_docker_jjoules_energy_medianes.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )
        print_to_file(
            '![docker_jjoules_energy](pictures/' + to_test_name(test) + '_docker_jjoules_instructions_medianes.png)\n\n', 
            prefix_folder_output_spino + 'README.md'
        )

    