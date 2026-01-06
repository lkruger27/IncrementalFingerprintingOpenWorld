import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns


#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams["figure.figsize"] = (6,4)

df_tls = pd.read_csv("./fingerprinting/results/RQ1_Budget_TLS.csv")
df_tls['implementations'] = 596
df_tls['benchmark'] = "TLS"
print(df_tls)

df_mqtt = pd.read_csv("./fingerprinting/results/RQ1_Budget_MQTT.csv")
df_mqtt['benchmark'] = "MQTT"
df_mqtt['implementations'] = 30
print(df_mqtt)

df_ssh = pd.read_csv("./fingerprinting/results/RQ1_Budget_SSH.csv")
df_ssh['benchmark'] = "SSH"
df_ssh['implementations'] = 100

df_ble = pd.read_csv("./fingerprinting/results/RQ1_Budget_BLE.csv")
df_ble['benchmark'] = "BLE"
df_ble['implementations'] = 40

df_blediff = pd.read_csv("./fingerprinting/results/RQ1_Budget_BLEDiff.csv")
df_blediff['benchmark'] = "BLEDiff"
df_blediff['implementations'] = 30

df = pd.concat([df_tls, df_ssh, df_mqtt, df_blediff, df_ble], ignore_index=True)
print(df)


df['misclassifications'] = 100 * (df['implementations'] - df['learned_models']) / df['implementations']
df['correct'] = 100 * df['learned_models'] / df['implementations']
df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

print(df.groupby(["benchmark","method"]).mean(numeric_only=True))

df = df[df["method"]!="IF-L#"]
df["method"] = df["method"].replace({"L#":"RL#", "AL#":"RAL#", "IF-AL#":"INFERNAL"})
df["benchmark"] = df["benchmark"].replace({"TLS":"TLS\n100000", "SSH":"SSH\n750000", "MQTT":"MQTT\n100000", "BLE":"BLE\n2500", "BLEDiff":"BLEDiff\n10000"})


g = sns.barplot(df, x="benchmark", y="correct", hue="method", errorbar=None)
g.set_ylabel("Correctly Learned (%)", fontsize=13)
g.set_ylim(0,105)
g.set_xlabel("Benchmark\nBudget",fontsize=13)
plt.yticks(fontsize=12, ticks=[0, 20, 40, 60, 80, 100], labels=["0", "20", "40", "60", "80", "100"])
plt.xticks(fontsize=12)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('./fingerprinting/plots/RQ1_budget.png', bbox_inches='tight')


