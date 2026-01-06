import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns


#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams["figure.figsize"] = (6,4)

df_tls = pd.read_csv("./fingerprinting/results/RQ3_TLS.csv")
df_tls['implementations'] = 596
df_tls['benchmark'] = "TLS"

df_mqtt = pd.read_csv("./fingerprinting/results/RQ3_MQTT.csv")
df_mqtt['benchmark'] = "MQTT"
df_mqtt['implementations'] = 30

df_ssh = pd.read_csv("./fingerprinting/results/RQ3_SSH.csv")
df_ssh['benchmark'] = "SSH"
df_ssh['implementations'] = 100

df_ble = pd.read_csv("./fingerprinting/results/RQ3_BLE.csv")
df_ble['benchmark'] = "BLE"
df_ble['implementations'] = 40

df_blediff = pd.read_csv("./fingerprinting/results/RQ3_BLEDiff.csv")
df_blediff['benchmark'] = "BLEDiff"
df_blediff['implementations'] = 30


df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)
df = df.drop(columns=['b'])
print(df_blediff.groupby(['oracle_type2']).mean(numeric_only=True).reset_index())

plot = 'rate'
if plot == 'nr':
    df['LCQ_FP'] = df['learning_fp'] 
    df['CQ_FP'] = df['matching_fp']
else:
    df['LCQ_FP'] = 100 * (df['learning_fp'] / df['TLCQ'])
    df['CQ_FP'] = 100 * (df['matching_fp'] / df['TFCQ'])
print(df.groupby(['benchmark', 'oracle_type2']).mean(numeric_only=True).reset_index())

df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

df_100_100 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp100')]
df_100_100 = df_100_100.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_50_50 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp50')]
df_50_50 = df_50_50.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_25_25 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp25')]
df_25_25 = df_25_25.groupby(['benchmark']).mean(numeric_only=True).reset_index()


X_plot = range(0, 100)
sns.scatterplot(data=df_100_100, x='LCQ_FP', y='CQ_FP', hue='benchmark', marker='s', s=100, edgecolor='black')
sns.scatterplot(data=df_50_50, x='LCQ_FP', y='CQ_FP', hue='benchmark', marker='p', s=100, edgecolor='black')
sns.scatterplot(data=df_25_25, x='LCQ_FP', y='CQ_FP', hue='benchmark', marker='o', s=100, edgecolor='black')
legend_elements = [Line2D([0], [0], lw=0, color='tab:red', marker='o', label='SSH'),
                   Line2D([0], [0], lw=0, color='tab:purple', marker='o', label='TLS'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', label='MQTT'),
                   Line2D([0], [0], lw=0, color='tab:blue', marker='o', label='BLE'),
                    Line2D([0], [0], lw=0, color='tab:orange', marker='o', label='BLEDiff'),
                   Line2D([0], [0], lw=0, color='k', marker='s', label='LCQ-100'),
                   Line2D([0], [0], lw=0, color='k', marker='p', label='LCQ-50'),
                   Line2D([0], [0], lw=0, color='k', marker='o', label='LCQ-25')]

plt.legend(handles=legend_elements, loc='best')
plt.ylabel("#FCQ Misclassifications / #FCQ Terminations", size=10)
plt.xlabel("#LCQ Misclassifications / #LCQ Terminations", size=10)
if plot == 'rate':
    plt.xlim(-2, 70)
    plt.ylim(-2, 40)
else: 
    plt.xlim(-2, 40)
    plt.ylim(-2, 40)
plt.savefig(f'./fingerprinting/plots/RQ3_{plot}.png', bbox_inches='tight')
