import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

def make_table_RQ0():
    df1 = pd.read_csv("./results/RQ0_closed_world_fingerprint_TLS.csv")
    df2 = pd.read_csv("./results/RQ0_IF_TLS.csv")
    df = pd.concat([df1, df2], ignore_index=True)

    df.replace('IF', '\\ifalg', inplace=True)
    df.replace('SepSeq', 'Fingerprint: SepSeq', inplace=True)
    df.replace('ADG', 'Fingerprint: ADG', inplace=True)

    df.sort_values(by=['start_specs'])
    df['misclassifications'] = 596 - df['correctly_learned_models'] - df['no_fingerprint']
    df['Total Symbols'] = df['fingerprint_queries'] + df['learning_queries'] + df['fingerprint_symbols'] + df['learning_symbols'] + df['conformance_queries'] + df['conformance_symbols']
    df['Fingerprint Symbols'] = df['fingerprint_queries']  + df['fingerprint_symbols'] 
    df['Learn Symbols'] = df['learning_queries'] + df['learning_symbols']
    df['Conformance Symbols'] = df['conformance_queries']  + df['conformance_symbols'] 

    df = df.groupby(['start_specs','algorithm']).mean(numeric_only=True).reset_index()
    df['Misclassifications'] = df.apply(lambda x: str(x['misclassifications']) + " - " + str(round(100*x['misclassifications']/596,1)) + "\%", axis=1)
    df['No Matches'] = df.apply(lambda x: str(x['no_fingerprint']) + " - " + str(round(100*x['no_fingerprint']/596,1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['correctly_learned_models'],1)) + " - " + str(round(100*x['correctly_learned_models']/596,1)) + "\%", axis=1)
    df = df[['algorithm','start_specs','Correct Models','Misclassifications','No Matches','Fingerprint Symbols','Conformance Symbols','Learn Symbols','Total Symbols']]
    
    print(df.to_latex(columns=['algorithm','start_specs','Correct Models','Misclassifications','No Matches','Fingerprint Symbols','Conformance Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrr'))

def make_table_RQ0_LSharp_TLS():
    df = pd.read_csv("./results/RQ0_LSharp_TLS.csv")

    df['Total Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']
    df['misclas'] = 100 * ((596 - df['learned_models']) / 596)

    df = df.groupby(['oracle_type1']).mean(numeric_only=True).reset_index()
    print(df)


def make_table_RQ1_Perfect_Knowledge():
    df_tls = pd.read_csv("./fingerprinting/results/RQ1_perfect_knowledge_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./fingerprinting/results/RQ1_perfect_knowledge_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./fingerprinting/results/RQ1_perfect_knowledge_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./fingerprinting/results/RQ1_perfect_knowledge_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./fingerprinting/results/RQ1_perfect_knowledge_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)
    df = df[df['method'] != 'IF-L#']

    df = df.groupby(['Benchmark','method']).mean(numeric_only=True).reset_index()

    df['Total Symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

    df['Fingerprint Symbols'] = df['total_separating_queries'] + df['total_separating_symbols'] 
    df['Learn Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']

    df = df.groupby(['Benchmark','method']).mean(numeric_only=True).reset_index()
    df['Algorithm'] = df['method']

    df.replace('AL#', '2\\adaptivelsharp', inplace=True)
    df.replace('L#', '1\\lsharp', inplace=True)
    df.replace('IF-AL#', '3\\ifalg', inplace=True)

    df_reordered = df[['Benchmark','Algorithm','Fingerprint Symbols','Learn Symbols','Total Symbols']]
    df_reordered = df_reordered.sort_values(by=['Benchmark','Algorithm'])
    df_reordered.replace('2\\adaptivelsharp', '\\adaptivelsharp', inplace=True)
    df_reordered.replace('1\\lsharp', '\\lsharp', inplace=True)
    df_reordered.replace('3\\ifalg', '\\ifalg', inplace=True)
    print(df_reordered)
    print(df_reordered.to_latex(columns=['Benchmark','Algorithm','Fingerprint Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrr'))


def make_table_RQ1_Budget():
    df_tls = pd.read_csv("./fingerprinting/results/RQ1_Budget_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./fingerprinting/results/RQ1_Budget_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./fingerprinting/results/RQ1_Budget_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./fingerprinting/results/RQ1_Budget_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./fingerprinting/results/RQ1_Budget_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)
    df = df[df['method'] != 'IF-L#']

    df['correctly_classified'] = df['learned_models']
    df['misclassifications'] =  df['implementations'] - df['learned_models']

    df = df.groupby(['Benchmark','method']).mean(numeric_only=True).reset_index()
    df['Correct Models'] = df.apply(lambda x: str(round(x['learned_models'],1)) + " - " + str(round(100*x['learned_models']/x['implementations'],1)) + "\%", axis=1)
    df['Algorithm'] = df['method']
    df['Budget'] = df['budget']

    df.replace('AL#', '2\\adaptivelsharp', inplace=True)
    df.replace('L#', '1\\lsharp', inplace=True)
    df.replace('IF-AL#', '3\\ifalg', inplace=True)

    df_reordered = df[['Benchmark','Algorithm','Budget','Correct Models']]
    df_reordered = df_reordered.sort_values(by=['Benchmark','Algorithm'])
    df_reordered.replace('2\\adaptivelsharp', '\\adaptivelsharp', inplace=True)
    df_reordered.replace('1\\lsharp', '\\lsharp', inplace=True)
    df_reordered.replace('3\\ifalg', '\\ifalg', inplace=True)
    # print(df_reordered)
    print(df_reordered.to_latex(columns=['Benchmark','Algorithm','Budget','Correct Models'],float_format="%.0f",index=False,column_format='lllr'))

def make_table_exp1():
    df_tls = pd.read_csv("./results/RQ1_RQ2_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./results/RQ1_RQ2_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./results/RQ1_RQ2_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./results/RQ1_RQ2_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./results/RQ1_RQ2_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

    df = df[((df['method']=='L#') & (df['oracle_type1']=='RandomWp100')) | ((df['method']=='AL#') & (df['oracle_type1']=='RandomWp100')) | ((df['method']=='IF-AL#') & (df['oracle_type1']=='RandomWp100') & (df['fingerprint_type']=='adg'))]
    print(df)

    df['correctly_classified'] = df['implementations'] - df['false_positives'] - df['false_negatives']
    df['misclassifications'] = df['false_positives'] + df['false_negatives']
    df['Total Symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

    df['Fingerprint Symbols'] = df['total_separating_queries'] + df['total_separating_symbols'] 
    df['MEQ Symbols'] = df['total_conformance_queries'] + df['total_conformance_symbols']
    df['Learn Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']

    df = df.groupby(['Benchmark','method']).mean(numeric_only=True).reset_index()
    df['FPs'] = df.apply(lambda x: str(x['false_positives']) + " - " + str(round(100*x['false_positives']/x['implementations'],1)) + "\%", axis=1)
    df['FNs'] = df.apply(lambda x: str(x['false_negatives']) + " - " + str(round(100*x['false_negatives']/x['implementations'],1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['learned_models'],1)) + " - " + str(round(100*x['learned_models']/x['implementations'],1)) + "\%", axis=1)
    df['Algorithm'] = df['method']

    df.replace('AL#', '2\\adaptivelsharp', inplace=True)
    df.replace('L#', '1\\lsharp', inplace=True)
    df.replace('IF-AL#', '3\\ifalg', inplace=True)

    df_reordered = df[['Benchmark','Algorithm','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols']]
    df_reordered = df_reordered.sort_values(by=['Benchmark','Algorithm'])
    df_reordered.replace('2\\adaptivelsharp', '\\adaptivelsharp', inplace=True)
    df_reordered.replace('1\\lsharp', '\\lsharp', inplace=True)
    df_reordered.replace('3\\ifalg', '\\ifalg', inplace=True)
    print(df_reordered)
    print(df_reordered.to_latex(columns=['Benchmark','Algorithm','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrrr'))

def make_table_exp2():
    df_tls = pd.read_csv("./results/RQ1_RQ2_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./results/RQ1_RQ2_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./results/RQ1_RQ2_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./results/RQ1_RQ2_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./results/RQ1_RQ2_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

    df = df[(df['method']=='IF-L#') | (df['method']=='IF-AL#')]
    df.replace('adg', 'ADG', inplace=True)
    df.replace('sep_seq', 'SepSeq', inplace=True)
    df.replace('IF-AL#', '\\adaptivelsharp', inplace=True)
    df.replace('IF-L#', '\\lsharp', inplace=True)
    df['Matching - Learning'] = df['fingerprint_type'] + ' - ' + df['oracle_type1'] + ' - ' + df['method']

    df['correctly_classified'] = df['implementations'] - df['false_positives'] - df['false_negatives']
    df['misclassifications'] = df['false_positives'] + df['false_negatives']
    df['Total Symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

    df['Fingerprint Symbols'] = df['total_separating_queries'] + df['total_separating_symbols'] 
    df['MEQ Symbols'] = df['total_conformance_queries'] + df['total_conformance_symbols']
    df['Learn Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']

    df = df.groupby(['Benchmark','Matching - Learning']).mean(numeric_only=True).reset_index()
    df['FPs'] = df.apply(lambda x: str(x['false_positives']) + " - " + str(round(100*x['false_positives']/x['implementations'],1)) + "\%", axis=1)
    df['FNs'] = df.apply(lambda x: str(x['false_negatives']) + " - " + str(round(100*x['false_negatives']/x['implementations'],1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['learned_models'],1)) + " - " + str(round(100*x['learned_models']/x['implementations'],1)) + "\%", axis=1)


    df_reordered = df[['Benchmark','Matching - Learning','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols']]
    df_reordered = df_reordered.sort_values(by=['Benchmark','Matching - Learning'])
    print(df_reordered.to_latex(columns=['Benchmark','Matching - Learning','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrrr'))

def make_table_exp2_additional():
    df_tls = pd.read_csv("./results/RQ2_additional_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./results/RQ2_additional_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./results/RQ2_additional_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./results/RQ2_additional_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./results/RQ2_additional_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

    df = df[(df['method']=='IF-L#') | (df['method']=='IF-AL#')]
    df.replace('adg', 'ADG', inplace=True)
    df.replace('sep_seq', 'SepSeq', inplace=True)
    df.replace('IF-AL#', '\\adaptivelsharp', inplace=True)
    df.replace('IF-L#', '\\lsharp', inplace=True)
    df['Matching - Learning'] = df['oracle_type1'] + ' - ' + df['oracle_type2']

    df.replace('RandomWp25 - RandomWp25', '1RandomWp25 - RandomWp25', inplace=True)
    df.replace('RandomWp25 - RandomWp50', '2RandomWp25 - RandomWp50', inplace=True)
    df.replace('RandomWp25 - RandomWp100', '3RandomWp25 - RandomWp100', inplace=True)
    df.replace('RandomWp50 - RandomWp25', '4RandomWp50 - RandomWp25', inplace=True)
    df.replace('RandomWp50 - RandomWp50', '5RandomWp50 - RandomWp50', inplace=True)
    df.replace('RandomWp50 - RandomWp100', '6RandomWp50 - RandomWp100', inplace=True)
    df.replace('RandomWp100 - RandomWp25', '7RandomWp100 - RandomWp25', inplace=True)
    df.replace('RandomWp100 - RandomWp50', '8RandomWp100 - RandomWp50', inplace=True)
    df.replace('RandomWp100 - RandomWp100', '9RandomWp100 - RandomWp100', inplace=True)

    df.sort_values(by=['Benchmark','Matching - Learning'])

    df['correctly_classified'] = df['implementations'] - df['false_positives'] - df['false_negatives']
    df['misclassifications'] = df['false_positives'] + df['false_negatives']
    df['Total Symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

    df['Fingerprint Symbols'] = df['total_separating_queries'] + df['total_separating_symbols'] 
    df['MEQ Symbols'] = df['total_conformance_queries'] + df['total_conformance_symbols']
    df['Learn Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']

    df = df.groupby(['Benchmark','Matching - Learning']).mean(numeric_only=True).reset_index()
    df['FPs'] = df.apply(lambda x: str(x['false_positives']) + " - " + str(round(100*x['false_positives']/x['implementations'],1)) + "\%", axis=1)
    df['FNs'] = df.apply(lambda x: str(x['false_negatives']) + " - " + str(round(100*x['false_negatives']/x['implementations'],1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['learned_models'],1)) + " - " + str(round(100*x['learned_models']/x['implementations'],1)) + "\%", axis=1)

    df = df[['Benchmark','Matching - Learning','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols']]
    df.replace('1RandomWp25 - RandomWp25', 'RandomWp25 - RandomWp25', inplace=True)
    df.replace('2RandomWp25 - RandomWp50', 'RandomWp25 - RandomWp50', inplace=True)
    df.replace('3RandomWp25 - RandomWp100', 'RandomWp25 - RandomWp100', inplace=True)
    df.replace('4RandomWp50 - RandomWp25', 'RandomWp50 - RandomWp25', inplace=True)
    df.replace('5RandomWp50 - RandomWp50', 'RandomWp50 - RandomWp50', inplace=True)
    df.replace('6RandomWp50 - RandomWp100', 'RandomWp50 - RandomWp100', inplace=True)
    df.replace('7RandomWp100 - RandomWp25', 'RandomWp100 - RandomWp25', inplace=True)
    df.replace('8RandomWp100 - RandomWp50', 'RandomWp100 - RandomWp50', inplace=True)
    df.replace('9RandomWp100 - RandomWp100', 'RandomWp100 - RandomWp100', inplace=True)
    print(df.to_latex(columns=['Benchmark','Matching - Learning','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrrr'))

def make_table_exp3():
    df_tls = pd.read_csv("./results/RQ3_TLS.csv")
    df_tls['implementations'] = 596
    df_tls['Benchmark'] = "TLS"

    df_mqtt = pd.read_csv("./results/RQ3_MQTT.csv")
    df_mqtt['Benchmark'] = "MQTT"
    df_mqtt['implementations'] = 30

    df_ssh = pd.read_csv("./results/RQ3_SSH.csv")
    df_ssh['Benchmark'] = "SSH"
    df_ssh['implementations'] = 100

    df_ble = pd.read_csv("./results/RQ3_BLE.csv")
    df_ble['Benchmark'] = "BLE"
    df_ble['implementations'] = 40

    df_blediff = pd.read_csv("./results/RQ3_BLEDiff.csv")
    df_blediff['Benchmark'] = "BLEDiff"
    df_blediff['implementations'] = 30

    df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

    df = df[(df['method']=='IF-L#') | (df['method']=='IF-AL#')]
    df.replace('adg', 'ADG', inplace=True)
    df.replace('sep_seq', 'SepSeq', inplace=True)
    df.replace('IF-AL#', '\\adaptivelsharp', inplace=True)
    df.replace('IF-L#', '\\lsharp', inplace=True)
    df['Matching - Learning'] = df['oracle_type1'] + ' - ' + df['oracle_type2']

    df.replace('RandomWp100 - RandomWp25', '7RandomWp100 - RandomWp25', inplace=True)
    df.replace('RandomWp100 - RandomWp50', '8RandomWp100 - RandomWp50', inplace=True)
    df.replace('RandomWp100 - RandomWp100', '9RandomWp100 - RandomWp100', inplace=True)

    df.sort_values(by=['Benchmark','Matching - Learning'])

    df['Total Symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

    df['Fingerprint Symbols'] = df['total_separating_queries'] + df['total_separating_symbols'] 
    df['MEQ Symbols'] = df['total_conformance_queries'] + df['total_conformance_symbols']
    df['Learn Symbols'] = df['total_learning_queries'] + df['total_learning_symbols']

    df = df.groupby(['Benchmark','Matching - Learning']).mean(numeric_only=True).reset_index()
    df['FFPs'] = df.apply(lambda x: str(x['matching_fp']) + " - " + str(round(100*x['matching_fp']/x['implementations'],1)) + "\%", axis=1)
    df['LFPs'] = df.apply(lambda x: str(x['learning_fp']) + " - " + str(round(100*x['learning_fp']/x['implementations'],1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['learned_models'],1)) + " - " + str(round(100*x['learned_models']/x['implementations'],1)) + "\%", axis=1)

    df = df[['Benchmark','Matching - Learning','FFPs','LFPs','Correct Models','FCQs','TFCQ','TLCQ','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols']]
    df.replace('7RandomWp100 - RandomWp25', 'RandomWp100 - RandomWp25', inplace=True)
    df.replace('8RandomWp100 - RandomWp50', 'RandomWp100 - RandomWp50', inplace=True)
    df.replace('9RandomWp100 - RandomWp100', 'RandomWp100 - RandomWp100', inplace=True)
    print(df.to_latex(columns=['Benchmark','Matching - Learning','FFPs','LFPs','Correct Models','FCQs','TFCQ','TLCQ','Fingerprint Symbols','FCQ Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrrrrrr'))

def make_table_duplicates():
    df = pd.read_csv("./results/duplicates_MQTT.csv")
    df['implementations'] = 6 + df['copies'] * 6

    df.sort_values(by=['algorithm','copies'])

    df['Total Symbols'] = df['fingerprint_queries'] + df['learning_queries'] + df['conformance_queries'] + df['conformance_symbols'] + df['fingerprint_symbols'] + df['learning_symbols']

    df['Fingerprint Symbols'] = df['fingerprint_queries']  + df['fingerprint_symbols'] 
    df['MEQ Symbols'] = df['conformance_queries'] + df['conformance_symbols']
    df['Learn Symbols'] = df['learning_queries'] + df['learning_symbols']

    df = df.groupby(['copies','algorithm']).mean(numeric_only=True).reset_index()
    df['FPs'] = df.apply(lambda x: str(x['false_positives']) + " - " + str(round(100*x['false_positives']/x['implementations'],1)) + "\%", axis=1)
    df['FNs'] = df.apply(lambda x: str(x['false_negatives']) + " - " + str(round(100*x['false_negatives']/x['implementations'],1)) + "\%", axis=1)
    df['Correct Models'] = df.apply(lambda x: str(round(x['correctly_learned_models'],1)) + " - " + str(round(100*x['correctly_learned_models']/x['implementations'],1)) + "\%", axis=1)
    
    df = df[['algorithm','copies','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols']]
    print(df.to_latex(columns=['algorithm','copies','Correct Models','Fingerprint Symbols','MEQ Symbols','Learn Symbols','Total Symbols'],float_format="%.0f",index=False,column_format='llrrrrrr'))


# make_table_RQ1_Budget()
# make_table_RQ1_Perfect_Knowledge()
# make_table_RQ0()
make_table_RQ0_LSharp_TLS()