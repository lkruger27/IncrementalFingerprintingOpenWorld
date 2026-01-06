import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns


#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams["figure.figsize"] = (6,3)
pd.options.display.float_format = '{:.0f}'.format

model = "SSH"
if model == "SSH":
    df1 = pd.read_csv("./fingerprinting/results/RQ1_RQ2_SSH.csv")
    df1= df1[(df1['method']=='AL#') & (df1['oracle_type1']=='RandomWp100') & (df1['oracle_type1'] == df1['oracle_type2'])]
    df2 = pd.read_csv("./fingerprinting/results/RQ1_additional_SSH.csv")
    df = pd.concat([df1, df2], ignore_index=True)
    df['benchmark'] = "SSH"
    df['implementations'] = 100
else:
    df = pd.read_csv("./fingerprinting/results/RQ1_additional_TLS.csv")
    df['benchmark'] = "TLS"
    df['implementations'] = 596


print(df.groupby(['method', 'oracle_type1', 'oracle_type2']).mean(numeric_only=True).reset_index())


df['misclassifications'] = 100 * (df['implementations'] - df['learned_models']) / df['implementations']
df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']

df_if = df[(df['method']=='IF-AL#') & (df['fingerprint_type']=='adg') & (df['oracle_type1'].str.contains('RandomWp')) & (df['oracle_type1'] == df['oracle_type2'])]
df_adaptivelsharp = df[(df['method']=='AL#') & (df['oracle_type1'].str.contains('RandomWp')) & (df['oracle_type1'] == df['oracle_type2'])]


print(df_adaptivelsharp[(df_adaptivelsharp['benchmark']=='TLS') & (df_adaptivelsharp['oracle_type1']=='RandomWp500')]['misclassifications'].std())
print(df_if[(df_if['benchmark']=='TLS') & (df_if['oracle_type1']=='RandomWp500')]['misclassifications'].std())

df_adaptivelsharp = df_adaptivelsharp.groupby(['oracle_type1']).mean(numeric_only=True).reset_index()
df_if = df_if.groupby(['oracle_type1']).mean(numeric_only=True).reset_index()

sns.scatterplot(data=df_if, x='misclassifications', y='total_symbols', color='tab:red', style="oracle_type1", markers={'RandomWp25': 's', 'RandomWp50': 'o', 'RandomWp100': '^', 'RandomWp200': '>', 'RandomWp500':'d'}, s=100, edgecolor='black')
sns.scatterplot(data=df_adaptivelsharp, x='misclassifications', y='total_symbols', color='tab:blue', style="oracle_type1", markers={'RandomWp25': 's', 'RandomWp50': 'o', 'RandomWp200': '>','RandomWp100': '^', 'RandomWp500':'d'}, s=100, edgecolor='black')
legend_elements = [Line2D([0], [0], lw=0, color='tab:red', marker='o', label='INFERNAL'),
                   Line2D([0], [0], lw=0, color='tab:blue', marker='o', label='RAL#'),
                   Line2D([0], [0], lw=0, color='k', marker='s', label='RandomWp25'),
                   Line2D([0], [0], lw=0, color='k', marker='o', label='RandomWp50'),
                   Line2D([0], [0], lw=0, color='k', marker='^', label='RandomWp100'),
                   Line2D([0], [0], lw=0, color='k', marker='>', label='RandomWp200'),
                   Line2D([0], [0], lw=0, color='k', marker='d', label='RandomWp500'),]
plt.legend(handles=legend_elements, loc='best')
plt.ylabel("Number of Symbols (log scale)")
plt.yscale('log',base=10) 
plt.xlim(left=-1)
plt.xlabel("Percentage of Misclassifications")
plt.savefig(f'./fingerprinting/plots/RQ1b_additional_{model}.png')


