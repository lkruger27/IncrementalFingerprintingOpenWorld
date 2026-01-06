import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import seaborn as sns
import itertools
from matplotlib.transforms import Bbox

#### ORACLE EXPERIMENTS ####
plt.rcParams['figure.constrained_layout.use'] = True
sns.set_theme(rc={'figure.figsize':(24,4)})
sns.set(font_scale = 1.5)
sns.set_style("whitegrid", {'axes.grid' : False})

def plot_rq_2(l):
    fig, axes = plt.subplots(1, 4)
    for (experiment, impls, a) in l:
        df = pd.read_csv(f'./fingerprinting/results/RQ1_RQ2_{experiment}.csv')
        df['implementations'] = impls
        df['benchmark'] = experiment

        df['misclassifications'] = 100 * (df['implementations'] - df['learned_models']) / df['implementations']
        df['total_symbols'] = df['total_separating_queries'] + df['total_conformance_queries'] + df['total_learning_queries'] + df['total_separating_symbols'] + df['total_conformance_symbols'] + df['total_learning_symbols']
        df['alg'] = df['oracle_type1'] + ' - ' + df['method']+ ' - ' + df['fingerprint_type']

        df = df[(df['method']=='IF-L#') | (df['method']=='IF-AL#')]
        df = df.groupby(['oracle_type1', 'method', 'fingerprint_type']).mean(numeric_only=True).reset_index()
        df.replace('adg', 'ADG', inplace=True)
        df.replace('sep_seq', 'SepSeq', inplace=True)
        print(df)

        mks = itertools.cycle(['o', '*', '^', 'd']) 
        
        hue = df[['oracle_type1', 'method']].apply(
        lambda row: f"{row.oracle_type1}, {row.method}", axis=1)
        hue.name = 'Equivalence query, Learning'
        hue_order = ['RandomWord1000, IF-AL#', 'RandomWord1000, IF-L#', 'RandomWp100, IF-AL#', 'RandomWp100, IF-L#', 'WpK, IF-AL#', 'WpK, IF-L#']
        style = df['fingerprint_type']
        style.name = 'Fingerprint'
        leg = False
        sns.scatterplot(data=df, x='misclassifications', y='total_symbols', hue=hue, hue_order = hue_order, style=style, palette=['tab:orange', '#ffbe86', 'tab:blue', '#8ebad9', 'tab:green', '#95cf95'], s = 100, markers=['o', '^'], edgecolor='black',ax=axes[a],legend=False)
        if a == 0:
            legend_elements = [Line2D([0], [0], lw=0, markersize=10, color='tab:orange', marker='o', label='RandomWord1000 - AL#'),
                   Line2D([0], [0], lw=0, markersize=10, color='#ffbe86', marker='o', label='RandomWord1000 - L#'),
                   Line2D([0], [0], lw=0, markersize=10, color='tab:blue', marker='o', label='RandomWp100 - AL#'),
                   Line2D([0], [0], lw=0, markersize=10, color='#8ebad9', marker='o', label='RandomWp100 - L#'),
                   Line2D([0], [0], lw=0, markersize=10, color='tab:green', marker='o', label='Wp2 - AL#'),
                   Line2D([0], [0], lw=0, markersize=10, color='#95cf95', marker='o', label='Wp2 - L#'),
                   Line2D([0], [0], lw=0, markersize=10, color='k', marker='o', label='ADG'),
                   Line2D([0], [0], lw=0, markersize=10, color='k', marker='^', label='SepSeq'),]
            axes[0].legend(handles=legend_elements, fancybox=True, ncol=8, bbox_to_anchor=(0., 1.1, 5.1, .102), mode='expand',handletextpad=0.01)
        axes[a].set_ylabel("Number of Symbols (log scale)", size=14)
        axes[a].set_yscale('log',base=10) 
        axes[a].set_xlabel(f"Percentage of Misclassifications {experiment}", size=14)
    plt.tight_layout()
    plt.subplots_adjust(wspace = 0.35)
    plt.subplots_adjust(hspace = 0.35)
    plt.savefig(f'./fingerprinting/plots/RQ2.png', bbox_inches='tight') 
    plt.close('all')

    
l = [('SSH',100,1), ('MQTT',30,2), ('TLS',596,0), ('BLEDiff',30,3)]
plot_rq_2(l)