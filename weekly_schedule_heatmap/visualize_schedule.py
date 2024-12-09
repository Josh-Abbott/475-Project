import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
from matplotlib.colors import ListedColormap
from datetime import datetime

def visualize_schedule(schedule_df, wrap_width=10, start_period=None, end_period=None):
    place_names = pd.unique(schedule_df.values.ravel('K'))
    place_names = [name for name in place_names if pd.notnull(name)]
    place_to_int = {name: idx for idx, name in enumerate(place_names)}
    int_to_place = {idx: name for name, idx in place_to_int.items()}

    schedule_numeric = schedule_df.replace(place_to_int)

    schedule_df_wrapped = schedule_df.applymap(
        lambda x: '\n'.join(textwrap.wrap(x, width=wrap_width)) if isinstance(x, str) else ''
    )

    num_places = len(place_to_int)
    palette = sns.color_palette("hls", num_places)
    cmap = ListedColormap(palette)
    cmap.set_bad(color='white')

    plt.figure(figsize=(14, 24))
    ax = sns.heatmap(
        schedule_numeric,
        cmap=cmap,
        cbar=False,
        annot=schedule_df_wrapped,
        fmt='',
        linewidths=0.5,
        linecolor='gray',
        annot_kws={"size": 8},
        square=False,
    )

    if start_period and end_period:
        try:
            start_date = datetime.strptime(start_period, '%Y-%m-%d').strftime('%B %d, %Y')
            end_date = datetime.strptime(end_period, '%Y-%m-%d').strftime('%B %d, %Y')
            title_text = f'Weekly Schedule Heatmap ({start_date} to {end_date})'
        except ValueError:
            title_text = f'Weekly Schedule Heatmap ({start_period} to {end_period})'
    else:
        title_text = 'Weekly Schedule Heatmap'

    wrapped_title = "\n".join(textwrap.wrap(title_text, width=50))

    plt.title(wrapped_title, fontsize=14)
    plt.xlabel('Day of Week', fontsize=14)
    plt.ylabel('Hour of Day', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    plt.show()
