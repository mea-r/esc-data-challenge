

THEMES = {
    "light": {
        "bg": "#F9FAFB",
        "paper": "#F3F4F6",
        "card_bg": "#FFFFFF",
        "text": "#2A3F5F",
        "subtext": "#6B7280",
        "grid": "#E5E7EB",
        "accent": "#2e6bff",
        "line_total": "#2A3F5F",
        "shading": "rgba(0, 0, 0, 0.03)",
        "annotation": "#2A3F5F"
    }
}


COLORS = {
    "PL": "#2e6bff",
    "EA": "#4cc9f0",
    "RU": "#ffcc00",
    "EX_RU": "#4B5563",
    "INVASION": "#ffcc00"
}

def get_theme(mode="light"):
    return THEMES["light"]

def apply_plot_theme(fig):

    if not fig:
        return fig
    
    TEXT_COLOR = "#2A3F5F"
    FONT_FAMILY = "Georgia"
    BG_COLOR = "#F3F4F6"
    
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(
            family=FONT_FAMILY,
            color=TEXT_COLOR,
            weight=600
        ),
        title=dict(
            font=dict(
                family=FONT_FAMILY,
                color=TEXT_COLOR,
                size=24,
                weight=600
            ),
            x=0.5,
            xanchor='center'
        ),
        legend=dict(
            font=dict(
                family=FONT_FAMILY,
                size=16,
                color=TEXT_COLOR
            )
        )
    )


    fig.update_xaxes(
        tickfont=dict(family=FONT_FAMILY, color=TEXT_COLOR, weight=600, size=16),
        title_font=dict(family=FONT_FAMILY, color=TEXT_COLOR, weight=600, size=18),
        tickprefix="<b>", ticksuffix="</b>"
    )
    fig.update_yaxes(
        tickfont=dict(family=FONT_FAMILY, color=TEXT_COLOR, weight=600, size=16),
        title_font=dict(family=FONT_FAMILY, color=TEXT_COLOR, weight=600, size=18),
        tickprefix="<b>", ticksuffix="</b>"
    )
    
    return fig
