import matplotlib.pyplot as plt
import pandas as pd
from colorcet import glasbey_light

from . import abc_load as abc


plt.rcParams.update({'font.size': 7})


def barplot_dual_y_count_frac(metrics_df, taxonomy_level, gt5_only=True):
    ''' Plot a barplot with both count and fraction of cells in each region.

    Parameters
    ----------
    metrics_df : pd.DataFrame
        DataFrame made with diversity_metrics.calculate_diversity_metrics()
    taxonomy_level : str, {'cluster', 'supertype', 'subclass'}
        ABC Atlas taxonomy level to plot
    gt5_only : bool
        If True, use the _gt5 columns for count and fraction
    '''
    # set metrics_df col based on thresholding to >5 cells or not
    count_col = f'count_gt5_{taxonomy_level}' if gt5_only else f'count_{taxonomy_level}'
    frac_col = f'frac_gt5_{taxonomy_level}' if gt5_only else f'frac_{taxonomy_level}'
    
    # sort regions so they're displayed low to high count, L to R
    metrics_df = metrics_df.sort_values(by=count_col, ascending=True)
    
    fig, ax1 = plt.subplots(figsize=(8,4))
    # Plot the absolute counts on the left y-axis
    ax1.scatter(metrics_df.index, metrics_df[count_col], 
                color='#5DA7E5', alpha=0)
    ax1.set_ylabel(f'unique {taxonomy_level} count', color='k')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.set_xticks(metrics_df.index)
    ax1.set_xticklabels(metrics_df.index, rotation=90)
    ax1.set_xlabel('CCF subregions')
    ax1.set_ylim(0, metrics_df[count_col].max()*1.05)
    plt.grid(visible=True, axis='y')

    # Plot the fraction values on the right y-axis
    ax2 = ax1.twinx()
    ax2.bar(metrics_df.index, metrics_df[frac_col], 
            color='#5DA7E5', label=taxonomy_level)
    # ntot = obs_neurons_ccf[taxonomy_level].value_counts().loc[lambda x: x>5].shape[0]
    ax2.set_ylabel(f'fraction of total {taxonomy_level} count', color='k', rotation=270, labelpad=15)
    ax2.set_ylim(0, metrics_df[frac_col].max()*1.05)
    ax2.tick_params(axis='y', labelcolor='k')
    

    plt.title(f'{taxonomy_level} count per CCF structure')
    return fig

def plot_metric_multiple_levels(metrics_df, 
                                metric, 
                                taxonomy_levels=['cluster','supertype','subclass'],
                                ylabel=None):

    if ylabel is None:
        ylabel = metric
    
    fig, ax1 = plt.subplots(figsize=(8,4))
    
    if taxonomy_levels==None:
        # enable plotting of a single metric
        metrics_df = metrics_df.sort_values(by=metric, ascending=True)
        ax1.scatter(metrics_df.index, metrics_df[metric], zorder=2)
    else:
        # sort by the metric of the first item in taxonomy_levels list
        metrics_df = metrics_df.sort_values(by="_".join([metric, 
                                                                taxonomy_levels[0]]), 
                                                   ascending=True)
        for level in taxonomy_levels[::-1]:
            ax1.scatter(metrics_df.index, 
                        metrics_df["_".join([metric, level])], 
                        label=level, zorder=2) 
        ax1.legend()

    ax1.set_xticks(metrics_df.index)
    ax1.set_xticklabels(metrics_df.index, rotation=90)
    ax1.set_xlabel('CCF structures')
    ax1.set_ylabel(ylabel)
    plt.grid(visible=True, axis='both', zorder=0, color='whitesmoke')
    
    return fig


def barplot_stacked_proportions(obs, taxonomy_level, ccf_metrics,
                                ccf_regions=None,
                                legend=True, palette=None,
                                min_cell_frac=0.01,
                                min_cell_count=None,
                                ordered_regions=None,
                                orientation='vertical'):
    """ Generate a stacked barplot showing the proportion of each taxonomy level
    category in each CCF region.
    
    Parameters
    ----------
    obs : pd.DataFrame
        dataframe of cells with CCF annotations & mapped taxonomy levels
    taxonomy_level : str, {'cluster', 'supertype', 'subclass'}
        ABC Atlas taxonomy level to plot
    ccf_metrics : pd.DataFrame
        DataFrame made with diversity_metrics.calculate_diversity_metrics()
    ccf_regions : list of str, default=None
        list of CCF regions to restrict the plot to
    legend : bool, default=True
        whether to display the legend
    palette : dict, default=None
        dictionary mapping taxonomy level categories to colors
    min_cell_frac : float, in range [0,1], default=0.01
        sets minimum fraction of cells required for a category to be included;
        categories <= this threshold are aggregated into an 'other' category
    min_cell_count : int, default=None, suggested=5
        sets minimum number of cells required for a category to be included; 
        categories <= this threshold are aggregated into an 'other' category.
        If set, it supercedes min_cell_frac
    ordered_regions : list of str, default=None
        list of CCF regions to plot, in the order they should be displayed
    orientation : str, {'vertical', 'horizontal'}, default='vertical'
        orientation of the barplot; 'vertical' displays regions on x-axis using
        'bar', 'horizontal' displays regions on the y-axis using 'barh'
        
    """
    # Set the palette
    if palette is None:
        try:
            palette = abc.get_taxonomy_palette(taxonomy_level)
        except ValueError:
            # if the level is not in the atlas, use glasbey_light
            palette = glasbey_light
    # add 'other' to the palette
    palette['other'] = 'lightgrey'

    # Calculate the proportion of each taxonomy level category per region
    proportions_df = calculate_level_proportions(obs, 
                                                 taxonomy_level, 
                                                 min_count=min_cell_count, 
                                                 min_frac=min_cell_frac)
    if ccf_regions is None:
        ccf_regions = proportions_df.index
    else:
        ccf_regions = list(set(ccf_regions) & set(proportions_df.index))                                                
    # filter to only the regions of interest
    proportions_df = proportions_df.loc[ccf_regions]
    # clean up category columns that now are all zeros post-filtering
    proportions_df = proportions_df.loc[:,(proportions_df!=0).any(axis=0)]

    # reorder the proportions df
    if ordered_regions is None:
        # Sort ccf_regions by # of non-zero categories & Inverse Simpson's Index
        nonzero_counts = (proportions_df.drop(columns=['other'])!=0).sum(axis=1)
        nonzero_counts.name = 'nonzero_counts'
        inverse_simpsons = ccf_metrics.loc[
                                ccf_regions,
                                f'inverse_simpsons_{taxonomy_level}']
        # combine two metrics into a df that we can sort by
        metrics_to_sort_by = pd.concat([nonzero_counts, inverse_simpsons], axis=1)
        sorted_regions = metrics_to_sort_by.sort_values(
                                by=['nonzero_counts', 
                                    f'inverse_simpsons_{taxonomy_level}'], 
                                ascending=[True, True]
                                ).index
    else:
        sorted_regions = ordered_regions
    proportions_df = proportions_df.loc[sorted_regions]

    # Plot stacked barplot, using barh or bar 
    if orientation=='horizontal':
        fig, ax = plt.subplots(1,1, figsize=(5,12))
        proportions_df.plot(kind='barh', stacked=True, ax=ax, legend=legend, 
                            color=palette)
        # axis formatting for horizontal barplot
        ax.set_yticklabels(proportions_df.index)
        ax.set_ylabel('CCF structure')
        ax.set_ylim(ax.get_ylim()[0]-0.3, ax.get_ylim()[1]+0.2) # make room for ax.text() annotations
        ax.invert_yaxis()  # put lowest-diversity region at the top
        ax.set_xlim(0,1.11)  # make room for ax.text() annotations
        ax.set_xlabel('proportion of cells in unique '+taxonomy_level)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ['0', '', '0.5', '', '1'])
        ax.tick_params(which='both', direction='in', top=True, labeltop=False)
    else:
        fig, ax = plt.subplots(1,1, figsize=(12,5))
        proportions_df.plot(kind='bar', stacked=True, ax=ax, legend=legend, 
                            color=palette)
        # axis formatting for vertical barplot
        ax.set_xticklabels(proportions_df.index, rotation=90)
        ax.set_xlabel('CCF structure')
        ax.set_xlim(ax.get_xlim()[0]-0.1, ax.get_xlim()[1]+0.1) # make room for ticks & text annotations
        ax.set_ylim(0,1.09)  # make room for ax.text() annotations
        ax.set_ylabel('proportion of cells in unique '+taxonomy_level)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ['0', '', '0.5', '', '1'])
        ax.tick_params(which='both', direction='in', right=True, labelright=False)
    
    # format legend
    if legend:
        # Reorder the legend labels alphabetically
        handles, labels = ax.get_legend_handles_labels()
        order = sorted(range(len(labels)), key=lambda k: labels[k])
        ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                  loc='upper left', bbox_to_anchor=(0, -0.3), ncol=2)

    # display the number of non-zero, non-other categories above each region's bar
    for i, region in enumerate(proportions_df.index):
        n_all = ccf_metrics.loc[region, f'count_{taxonomy_level}']
        n_nonzero = (proportions_df.loc[region, proportions_df.columns!='other']>0).sum()
        if orientation=='horizontal':
            ax.text(1.02, i, f'{n_nonzero}', verticalalignment='center',
                    horizontalalignment='left')
        else:
            ax.text(i, 1.02, f'{n_all}/n({n_nonzero})', horizontalalignment='center')

    return fig


def calculate_level_proportions(obs, 
                                taxonomy_level,
                                ccf_label='parcellation_structure_eroded',
                                min_frac=0.01,
                                min_count=None):
    ''' Calculate the proportion of each level in each CCF region for a stacked 
    barplot.

    Parameters
    ----------
    obs : pd.DataFrame
        dataframe of cells with CCF annotations & mapped taxonomy levels
    taxonomy_level : str, {'cluster', 'supertype', 'subclass'}
        ABC Atlas taxonomy level 
    ccf_label : str, default='parcellation_structure_eroded'
        column name in obs_ccf where the CCF annotations can be found
    min_frac : float, in range [0,1], default=0.01
        sets minimum fraction of cells required for a category to be included;
        categories <= this threshold are aggregated into an 'other' category
    min_count : int, default=None, suggested=5
        sets minimum number of cells required for a category to be included; 
        categories <= this threshold are aggregated into an 'other' category
        If set, it supercedes min_frac

    Returns
    -------
    proportions_df : pd.DataFrame
        df with the proportion of each taxonomy_level in each CCF region, where
        index=obs_ccf[ccf_label].unique(), columns=obs_ccf[taxonomy_level].unique()
    '''
    # count the number of cells in each (structure, taxonomy_level) pair & save as a df  
    # where index=ccf_label & columns=taxonomy_level
    counts_df = obs.groupby([ccf_label, taxonomy_level], observed=True
                            ).size().unstack(fill_value=0)
    
    # if min_count is set, it supercedes min_frac
    if min_count is not None:
        to_other = (counts_df <= min_count)
    else:
        # Calculate the fraction of each category, per region
        total_counts = counts_df.sum(axis=1)
        fraction_df = counts_df.div(total_counts, axis=0)
        # Get categories to move to 'other'
        to_other = (fraction_df <= min_frac)
    
    # Aggregate & move counts below threshold to 'other' column
    other_col_df = counts_df[to_other].sum(axis=1)
    counts_df = counts_df[~to_other]  # replace counts below threshold with NaN
    counts_df = counts_df.join(other_col_df.rename('other')).fillna(0)
    # clean up columns that are not empty
    counts_df = counts_df.loc[:,(counts_df!=0).any(axis=0)]

    # calculate proportions from counts
    proportions_df = counts_df.div(counts_df.sum(axis=1), axis=0)

    return proportions_df

