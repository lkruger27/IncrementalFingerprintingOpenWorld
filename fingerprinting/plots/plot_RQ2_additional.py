import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns


#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams["figure.figsize"] = (6,3)

df_tls = pd.read_csv("./fingerprinting/results/RQ2_additional_TLS.csv")
df_tls['implementations'] = 596
df_tls['benchmark'] = "TLS"

df_mqtt = pd.read_csv("./fingerprinting/results/RQ2_additional_MQTT.csv")
df_mqtt['benchmark'] = "MQTT"
df_mqtt['implementations'] = 30


df_ssh = pd.read_csv("./fingerprinting/results/RQ2_additional_SSH.csv")
df_ssh['benchmark'] = "SSH"
df_ssh['implementations'] = 100

df_ble = pd.read_csv("./fingerprinting/results/RQ2_additional_BLE.csv")
df_ble['benchmark'] = "BLE"
df_ble['implementations'] = 40

df_blediff = pd.read_csv("./fingerprinting/results/RQ2_additional_BLEDiff.csv")
df_blediff['benchmark'] = "BLEDiff"
df_blediff['implementations'] = 30

df = pd.concat([df_tls, df_ssh, df_mqtt, df_ble, df_blediff], ignore_index=True)

df['misclassifications'] = 100 * (df['implementations'] - df['learned_models']) / df['implementations']
print(df.groupby(['benchmark', 'oracle_type1', 'oracle_type2']).mean(numeric_only=True).reset_index())
print(df.groupby(['benchmark', 'oracle_type2', 'oracle_type1']).mean(numeric_only=True).reset_index())

df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

df_100_100 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp100')]
df_100_100 = df_100_100.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_100_50 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp50')]
df_100_50 = df_100_50.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_100_25 = df[(df['oracle_type1']=='RandomWp100') & (df['oracle_type2']=='RandomWp25')]
df_100_25 = df_100_25.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_50_100 = df[(df['oracle_type1']=='RandomWp50') & (df['oracle_type2']=='RandomWp100')]
df_50_100 = df_50_100.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_50_50 = df[(df['oracle_type1']=='RandomWp50') & (df['oracle_type2']=='RandomWp50')]
df_50_50 = df_50_50.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_50_25 = df[(df['oracle_type1']=='RandomWp50') & (df['oracle_type2']=='RandomWp25')]
df_50_25 = df_50_25.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_25_100 = df[(df['oracle_type1']=='RandomWp25') & (df['oracle_type2']=='RandomWp100')]
df_25_100 = df_25_100.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_25_50 = df[(df['oracle_type1']=='RandomWp25') & (df['oracle_type2']=='RandomWp50')]
df_25_50 = df_25_50.groupby(['benchmark']).mean(numeric_only=True).reset_index()

df_25_25 = df[(df['oracle_type1']=='RandomWp25') & (df['oracle_type2']=='RandomWp25')]
df_25_25 = df_25_25.groupby(['benchmark']).mean(numeric_only=True).reset_index()

sns.scatterplot(data=df_100_100, x='misclassifications', y='total_symbols', hue='benchmark', marker='s', s=100, edgecolor='black')
sns.scatterplot(data=df_100_50, x='misclassifications', y='total_symbols', hue='benchmark', marker='p', s=100, edgecolor='black')
sns.scatterplot(data=df_100_25, x='misclassifications', y='total_symbols', hue='benchmark', marker='o', s=100, edgecolor='black')
sns.scatterplot(data=df_50_100, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.6, marker='s', s=100, edgecolor='black')
sns.scatterplot(data=df_50_50, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.6, marker='p', s=100, edgecolor='black')
sns.scatterplot(data=df_50_25, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.6, marker='o', s=100, edgecolor='black')
sns.scatterplot(data=df_25_100, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.3, marker='s', s=100, edgecolor='black')
sns.scatterplot(data=df_25_50, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.3, marker='p', s=100, edgecolor='black')
sns.scatterplot(data=df_25_25, x='misclassifications', y='total_symbols', hue='benchmark', alpha=0.3, marker='o', s=100, edgecolor='black')
legend_elements = [Line2D([0], [0], lw=0, color='tab:red', marker='o', label='SSH'),
                   Line2D([0], [0], lw=0, color='tab:purple', marker='o', label='TLS'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', label='MQTT'),
                   Line2D([0], [0], lw=0, color='tab:blue', marker='o', label='BLE'),
                   Line2D([0], [0], lw=0, color='tab:orange', marker='o', label='BLEDiff'),
                   Line2D([0], [0], lw=0, color='k', marker='s', label='LCQ-100'),
                   Line2D([0], [0], lw=0, color='k', marker='p', label='LCQ-50'),
                   Line2D([0], [0], lw=0, color='k', marker='o', label='LCQ-25'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', label='FCQ-100'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', alpha=0.6, label='FCQ-50'),
                   Line2D([0], [0], lw=0, color='tab:green', marker='o', alpha=0.3, label='FCQ-25'),]
plt.legend(handles=legend_elements, loc='best')
plt.ylabel("Number of Symbols (log scale)")
plt.yscale('log',base=10) 
plt.xlabel("Percentage of Misclassifications")
plt.savefig('./fingerprinting/plots/RQ2_additional.png')
