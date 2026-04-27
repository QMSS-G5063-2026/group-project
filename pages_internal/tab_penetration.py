"""
Tab -- Co-occurrence
Owner: Team Member B (Xiang Fan)

Evidence question: Does AI behave as a separate trend, or does it grow
*inside* the other trends?

Charts:
  1. AI overlap bar chart: how many companies are tagged AI + each reference trend
  2. Metric cards: coexistence rate for each reference trend in the latest year
  3. AI coexistence rate over time (3-line chart)
  4. Tag co-occurrence network (inside expander, with year slider)
  5. Finding callout
"""

import math

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import utils

# Map coexistence column names to their display colors
_LINE_COLORS = {
    'AI in Enterprise SaaS': utils.COLORS['Enterprise SaaS'],
    'AI in Fintech':          utils.COLORS['Fintech'],
    'AI in Developer Tools':  utils.COLORS['Developer Tools'],
}


def render(df):
    coexistence = utils.compute_ai_coexistence(df)
    last_year   = int(coexistence.index.max())

    saas_latest     = coexistence.loc[last_year, 'AI in Enterprise SaaS']
    fintech_latest  = coexistence.loc[last_year, 'AI in Fintech']
    devtools_latest = coexistence.loc[last_year, 'AI in Developer Tools']

    # --------------------------------------------------------------------------
    # Chart 1: AI overlap bar -- how many companies are AI AND each ref trend
    # --------------------------------------------------------------------------
    st.markdown(
        '<div style="font-size:17px; font-weight:600; color:#111;">'
        'How many companies belong to AI <em>and</em> a reference trend?</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        'A company can carry multiple tags. '
        'High overlap means AI has grown *inside* that trend, not beside it.'
    )

    # Build ALL pairwise overlaps (6 pairs for 4 trends) so we can compare
    # AI+X overlaps against reference-trend cross-overlaps in one chart.
    all_trends = utils.TREND_NAMES  # ['AI', 'Enterprise SaaS', 'Fintech', 'Developer Tools']
    pairs = []
    for i, t1 in enumerate(all_trends):
        for t2 in all_trends[i + 1:]:
            n_t1    = int(df[utils.trend_col(t1)].sum())
            n_t2    = int(df[utils.trend_col(t2)].sum())
            n_both  = int((df[utils.trend_col(t1)] & df[utils.trend_col(t2)]).sum())
            # Express as % of the SMALLER trend (conservative / directional)
            pct     = n_both / max(min(n_t1, n_t2), 1) * 100
            involves_ai = (t1 == 'AI' or t2 == 'AI')
            label = f'AI + {t2}' if t1 == 'AI' else f'{t1} + {t2}'
            pairs.append({
                'Pair':          label,
                'Companies':     n_both,
                'Pct of smaller': round(pct, 1),
                'Involves AI':   involves_ai,
            })
    pairs_df = pd.DataFrame(pairs).sort_values('Pct of smaller', ascending=True)

    # Color: orange for AI pairs, gray for reference-only pairs
    bar_colors = [
        utils.COLORS['AI'] if row['Involves AI'] else '#CCCCCC'
        for _, row in pairs_df.iterrows()
    ]

    fig_ov = go.Figure()
    fig_ov.add_trace(go.Bar(
        x=pairs_df['Pct of smaller'],
        y=pairs_df['Pair'],
        orientation='h',
        marker_color=bar_colors,
        text=[f"{v:.0f}%" for v in pairs_df['Pct of smaller']],
        textposition='outside',
        customdata=pairs_df[['Companies', 'Pct of smaller']].values,
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Companies in both: %{customdata[0]}<br>'
            'Share of smaller trend: %{customdata[1]:.0f}%'
            '<extra></extra>'
        ),
    ))
    fig_ov.update_layout(
        height=340,
        template='plotly_white',
        xaxis=dict(title='% of smaller trend also tagged with the other',
                   ticksuffix='%', range=[0, 110]),
        yaxis=dict(automargin=True, title=None),
        margin=dict(l=20, r=60, t=30, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
    )
    # Annotation to highlight AI pairs
    fig_ov.add_annotation(
        xref='paper', yref='paper',
        x=1.0, y=0.05,
        text='<span style="color:#E6550D;">Orange = involves AI</span>',
        showarrow=False,
        font=dict(size=11, color=utils.COLORS['AI']),
        xanchor='right',
    )
    st.plotly_chart(fig_ov, width="stretch")

    # Summary stats panel (right of chart was replaced by integrated chart above)
    overlap_data = [
        {
            'Category':        trend,
            'Overlap':         f'AI + {trend}',
            'Companies':       int((df['is_AI'] & df[utils.trend_col(trend)]).sum()),
            'Total in trend':  int(df[utils.trend_col(trend)].sum()),
        }
        for trend in utils.REFERENCE_TRENDS
    ]
    overlap_df = pd.DataFrame(overlap_data)
    overlap_df['AI share of trend'] = (
        overlap_df['Companies'] / overlap_df['Total in trend'] * 100
    ).round(1)

    cols = st.columns(3)
    for col, (_, row) in zip(cols, overlap_df.iterrows()):
        color = utils.COLORS[row['Category']]
        col.markdown(
            f'<div style="border-left: 4px solid {color}; '
            f'padding: 8px 14px; background: #FAFAFA;">'
            f'<span style="font-size:12px; color:#888;">{row["Category"]}</span><br>'
            f'<span style="font-size:24px; font-weight:700; color:#111;">'
            f'{row["AI share of trend"]:.0f}%</span>'
            f'<span style="font-size:12px; color:#888;"> also tagged AI</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # Metric cards: latest-year coexistence rates
    # --------------------------------------------------------------------------
    st.markdown(
        f'<div style="margin-top:28px; font-size:17px; font-weight:600; color:#111;">'
        f'Coexistence rate in {last_year}: share of each trend cohort also tagged AI</div>',
        unsafe_allow_html=True,
    )

    # Early-year baseline for delta display
    baseline_year = 2014 if 2014 in coexistence.index else int(coexistence.index.min())
    saas_base     = coexistence.loc[baseline_year, 'AI in Enterprise SaaS']
    saas_change   = saas_latest - saas_base  # positive = grown

    col1, col2, col3 = st.columns(3)
    col1.metric(
        f'AI in Enterprise SaaS ({last_year})',
        f'{saas_latest:.0f}%',
        f'+{saas_change:.0f} pts since {baseline_year}',
    )
    col2.metric(f'AI in Fintech ({last_year})',          f'{fintech_latest:.0f}%')
    col3.metric(f'AI in Developer Tools ({last_year})',  f'{devtools_latest:.0f}%')

    # --------------------------------------------------------------------------
    # Chart 2: Coexistence rate over time (3 lines)
    # --------------------------------------------------------------------------
    st.markdown(
        '<div style="margin-top:28px; font-size:17px; font-weight:600; color:#111;">'
        'Coexistence rate over time</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        'For each year: share of Enterprise SaaS / Fintech / Developer Tools companies '
        'in that YC batch that also carry an AI tag.'
    )

    fig = go.Figure()
    for col_name, color in _LINE_COLORS.items():
        fig.add_trace(go.Scatter(
            x=coexistence.index,
            y=coexistence[col_name],
            mode='lines+markers',
            name=col_name,
            line=dict(width=3, color=color),
            marker=dict(size=7),
            hovertemplate='%{x}: %{y:.1f}%<extra>' + col_name + '</extra>',
        ))

    fig.add_vline(x=2022, line_dash='dash', line_color='#CCCCCC', opacity=0.8)
    fig.add_annotation(
        x=2022, y=95,
        text='ChatGPT launched',
        showarrow=False,
        font=dict(size=10, color='#aaa'),
        xanchor='left',
        xshift=6,
    )

    fig.update_layout(
        height=440,
        xaxis_title=None,
        yaxis=dict(
            title='Share of trend cohort also tagged AI',
            range=[0, 100],
            ticksuffix='%',
            gridcolor='#F0F0F0',
        ),
        hovermode='x unified',
        legend_title_text='Reference trend',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=20),
    )

    st.plotly_chart(fig, width="stretch")

    # --------------------------------------------------------------------------
    # Chart 3: Tag co-occurrence network (expander)
    # --------------------------------------------------------------------------
    with st.expander('Tag co-occurrence network (interactive)'):
        st.markdown(
            'Node size = number of companies carrying that tag. '
            'Node color = share of those companies also tagged AI '
            '(orange = high AI share, blue = low). '
            'Use the year slider to see how the network evolved.'
        )

        year = st.slider(
            'Year',
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=last_year,
            key='coexistence_year_slider',
        )

        edges, nodes = utils.compute_cooccurrence(df, year=year, top_n=30, min_count=2)

        if not nodes:
            st.warning('No network data available for this year.')
        else:
            tags    = list(nodes.keys())
            n_nodes = len(tags)

            positions = {
                tag: (
                    1.2 * math.cos(2 * math.pi * i / max(n_nodes, 1)),
                    1.2 * math.sin(2 * math.pi * i / max(n_nodes, 1)),
                )
                for i, tag in enumerate(tags)
            }

            # Edges
            edge_x, edge_y = [], []
            for edge in edges:
                t1, t2 = edge.get('tag1'), edge.get('tag2')
                if t1 in positions and t2 in positions:
                    x0, y0 = positions[t1]
                    x1, y1 = positions[t2]
                    edge_x += [x0, x1, None]
                    edge_y += [y0, y1, None]

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=1.2, color='rgba(120,120,120,0.30)'),
                hoverinfo='none',
            )

            # Nodes
            node_x, node_y, node_size, node_color, node_text = [], [], [], [], []
            for tag in tags:
                x, y  = positions[tag]
                info  = nodes[tag]
                n_co  = info.get('n_companies', 1)
                ai_pc = info.get('ai_pct', 0)
                node_x.append(x)
                node_y.append(y)
                node_size.append(max(int(n_co ** 0.5) * 5, 10))
                node_color.append(ai_pc)
                node_text.append(
                    f"Tag: <b>{tag}</b><br>Companies: {n_co}<br>AI share: {ai_pc:.1f}%"
                )

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=tags,
                textposition='top center',
                textfont=dict(size=11),
                hovertext=node_text,
                hoverinfo='text',
                marker=dict(
                    size=node_size,
                    color=node_color,
                    colorscale='Oranges',
                    cmin=0, cmax=100,
                    showscale=True,
                    colorbar=dict(title='AI share %', thickness=14),
                    line=dict(width=1, color='#ccc'),
                ),
            )

            net_fig = go.Figure(data=[edge_trace, node_trace])
            net_fig.update_layout(
                title=f'Tag co-occurrence network -- {year}',
                showlegend=False,
                height=600,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                paper_bgcolor='white',
            )
            st.plotly_chart(net_fig, width="stretch")

    # --------------------------------------------------------------------------
    # Finding
    # --------------------------------------------------------------------------
    utils.finding_box(
        f'<strong>Past trends coexisted as parallel sectors. AI does not.</strong><br>'
        f'By {last_year}, AI appears inside <strong>{saas_latest:.0f}%</strong> of '
        f'Enterprise SaaS companies, <strong>{fintech_latest:.0f}%</strong> of Fintech, '
        f'and <strong>{devtools_latest:.0f}%</strong> of Developer Tools. '
        f'AI is not a sector growing alongside others -- it is a horizontal layer '
        f'growing through all of them simultaneously.'
    )
