import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns


#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams["figure.figsize"] = (6,4)

df_tls = pd.read_csv("./fingerprinting/results/RQ1_RQ2_TLS.csv")
df_tls['implementations'] = 596
df_tls['benchmark'] = "TLS"

df_mqtt = pd.read_csv("./fingerprinting/results/RQ1_RQ2_MQTT.csv")
df_mqtt['benchmark'] = "MQTT"
df_mqtt['implementations'] = 30

df_ssh = pd.read_csv("./fingerprinting/results/RQ1_RQ2_SSH.csv")
df_ssh['benchmark'] = "SSH"
df_ssh['implementations'] = 100

df_ble = pd.read_csv("./fingerprinting/results/RQ1_RQ2_BLE.csv")
df_ble['benchmark'] = "BLE"
df_ble['implementations'] = 40

df_blediff = pd.read_csv("./fingerprinting/results/RQ1_RQ2_BLEDiff.csv")
df_blediff['benchmark'] = "BLEDiff"
df_blediff['implementations'] = 30

df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

df['correctly_classified'] = df['implementations'] - df['false_positives'] - df['false_negatives']
df['misclassifications'] = 100 * (df['implementations'] - df['learned_models']) / df['implementations']
df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

df_lsharp = df[(df['method']=='L#') & (df['oracle_type1']=='RandomWp100')]
df_adaptivelsharp = df[(df['method']=='AL#') & (df['oracle_type1']=='RandomWp100')]
df_if = df[(df['method']=='IF-AL#') & (df['oracle_type1']=='RandomWp100') & (df['fingerprint_type']=='adg')]

df_if_yerr = [df_if[df_if['benchmark']=='BLEDiff']['total_symbols'].std(), df_if[df_if['benchmark']=='BLE']['total_symbols'].std(), df_if[df_if['benchmark']=='MQTT']['total_symbols'].std(), df_if[df_if['benchmark']=='SSH']['total_symbols'].std(), df_if[df_if['benchmark']=='TLS']['total_symbols'].std()]
df_if_xerr = [df_if[df_if['benchmark']=='BLEDiff']['misclassifications'].std(), df_if[df_if['benchmark']=='BLE']['misclassifications'].std(), df_if[df_if['benchmark']=='MQTT']['misclassifications'].std(), df_if[df_if['benchmark']=='SSH']['misclassifications'].std(), df_if[df_if['benchmark']=='SSH']['misclassifications'].std()]

df_lsharp_yerr = [df_lsharp[df_lsharp['benchmark']=='BLEDiff']['total_symbols'].std(), df_lsharp[df_lsharp['benchmark']=='BLE']['total_symbols'].std(), df_lsharp[df_lsharp['benchmark']=='MQTT']['total_symbols'].std(), df_lsharp[df_lsharp['benchmark']=='SSH']['total_symbols'].std(), df_lsharp[df_lsharp['benchmark']=='TLS']['total_symbols'].std()]
df_lsharp_xerr = [df_lsharp[df_lsharp['benchmark']=='BLEDiff']['misclassifications'].std(), df_lsharp[df_lsharp['benchmark']=='BLE']['misclassifications'].std(), df_lsharp[df_lsharp['benchmark']=='MQTT']['misclassifications'].std(), df_lsharp[df_lsharp['benchmark']=='SSH']['misclassifications'].std(), df_lsharp[df_lsharp['benchmark']=='TLS']['misclassifications'].std()]

df_adaptivelsharp_yerr = [df_adaptivelsharp[df_adaptivelsharp['benchmark']=='BLEDiff']['total_symbols'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='BLE']['total_symbols'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='MQTT']['total_symbols'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='SSH']['total_symbols'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='TLS']['total_symbols'].std()]
df_adaptivelsharp_xerr = [df_adaptivelsharp[df_adaptivelsharp['benchmark']=='BLEDiff']['misclassifications'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='BLE']['misclassifications'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='MQTT']['misclassifications'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='SSH']['misclassifications'].std(), df_adaptivelsharp[df_adaptivelsharp['benchmark']=='TLS']['misclassifications'].std()]

df_lsharp = df_lsharp.groupby(['benchmark']).mean(numeric_only=True).reset_index()
df_adaptivelsharp = df_adaptivelsharp.groupby(['benchmark']).mean(numeric_only=True).reset_index()
df_if = df_if.groupby(['benchmark']).mean(numeric_only=True).reset_index()
print(df_adaptivelsharp)
print(df_if)

sns.scatterplot(data=df_if, x='misclassifications', y='total_symbols', hue='benchmark', marker='d', s=100, edgecolor='black')
plt.errorbar(df_if['misclassifications'], df_if['total_symbols'], yerr=df_if_yerr, xerr=df_if_xerr, fmt='', ecolor='black', linestyle='')
sns.scatterplot(data=df_lsharp, x='misclassifications', y='total_symbols', hue='benchmark', marker='s', s=100, edgecolor='black')
plt.errorbar(df_lsharp['misclassifications'], df_lsharp['total_symbols'], yerr=df_lsharp_yerr, xerr=df_lsharp_xerr, fmt='', ecolor='black', linestyle='')
sns.scatterplot(data=df_adaptivelsharp, x='misclassifications', y='total_symbols', hue='benchmark', marker='^', s=100, edgecolor='black')
plt.errorbar(df_adaptivelsharp['misclassifications'], df_adaptivelsharp['total_symbols'], yerr=df_adaptivelsharp_yerr, xerr=df_adaptivelsharp_xerr, fmt='', ecolor='black', linestyle='')
legend_elements = [Line2D([0], [0], lw=0, color='tab:red', marker='o', label='SSH'),
                   Line2D([0], [0], lw=0, color='tab:purple', marker='o', label='TLS'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', label='MQTT'),
                   Line2D([0], [0], lw=0, color='tab:blue', marker='o', label='BLE'),
                   Line2D([0], [0], lw=0, color='tab:orange', marker='o', label='BLEDiff'),
                   Line2D([0], [0], lw=0, color='k', marker='d', label='INFERNAL'),
                   Line2D([0], [0], lw=0, color='k', marker='s', label='RL#'),
                   Line2D([0], [0], lw=0, color='k', marker='^', label='RAL#'),]
plt.legend(handles=legend_elements, loc='lower right')
plt.ylabel("Number of Symbols (log scale)",fontsize=13)
plt.yscale('log',base=10) 
plt.xlim(left=-1)
plt.xlabel("Percentage of Misclassifications\n",fontsize=13)
plt.yticks(fontsize=12)
plt.xticks(fontsize=12, ticks=[0, 10, 20, 30, 40, 50, 60, 70, 80], labels=["0\n", "10", "20", "30", "40", "50", "60", "70", "80"])
plt.tight_layout()
plt.savefig('./fingerprinting/plots/RQ1.png', bbox_inches='tight')


