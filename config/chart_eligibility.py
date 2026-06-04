"""Source of truth: which analytical types each chart requires."""

from typing import TypedDict


class ChartSpec(TypedDict):
    label: str
    description: str
    x: list[str]
    y: list[str]
    color: list[str]
    size: list[str]
    requires_multiple_y: bool
    min_numeric_for_corr: int


CHART_ELIGIBILITY: dict[str, ChartSpec] = {
    "histogram": {
        "label": "Histogram",
        "description": "Distribution of one continuous variable",
        "x": ["CONTINUOUS"],
        "y": [],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "bar": {
        "label": "Bar Chart",
        "description": "Compare categories or aggregated values",
        "x": ["CATEGORICAL"],
        "y": ["CONTINUOUS", "NONE"],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "scatter": {
        "label": "Scatter Plot",
        "description": "Relationship between two continuous variables",
        "x": ["CONTINUOUS"],
        "y": ["CONTINUOUS"],
        "color": ["CATEGORICAL", "CONTINUOUS", "NONE"],
        "size": ["CONTINUOUS", "NONE"],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "line": {
        "label": "Line Chart",
        "description": "Trend over time or ordered axis",
        "x": ["TEMPORAL", "CONTINUOUS_ORDERED"],
        "y": ["CONTINUOUS"],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "box": {
        "label": "Box Plot",
        "description": "Compare distribution summaries across groups",
        "x": ["CATEGORICAL"],
        "y": ["CONTINUOUS"],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "violin": {
        "label": "Violin Plot",
        "description": "Full distribution shape per category",
        "x": ["CATEGORICAL"],
        "y": ["CONTINUOUS"],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "pie": {
        "label": "Pie Chart",
        "description": "Part-to-whole for few categories (≤8 recommended)",
        "x": ["CATEGORICAL"],
        "y": ["CONTINUOUS", "NONE"],
        "color": [],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "heatmap_crosstab": {
        "label": "Heatmap (Cross-tab)",
        "description": "Two categorical variables — count or aggregate",
        "x": ["CATEGORICAL"],
        "y": ["CATEGORICAL"],
        "color": [],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "heatmap_correlation": {
        "label": "Correlation Heatmap",
        "description": "Pearson/Spearman matrix for numerical features",
        "x": [],
        "y": [],
        "color": [],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 2,
    },
    "scatter_matrix": {
        "label": "Pair Plot (Scatter Matrix)",
        "description": "All pairwise relationships (max 8 columns)",
        "x": [],
        "y": [],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 3,
    },
    "treemap": {
        "label": "Treemap",
        "description": "Hierarchical part-to-whole",
        "x": ["CATEGORICAL"],
        "y": ["CONTINUOUS"],
        "color": [],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "timeseries": {
        "label": "Time Series",
        "description": "Trend over datetime with range slider",
        "x": ["TEMPORAL"],
        "y": ["CONTINUOUS"],
        "color": ["CATEGORICAL", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "candlestick": {
        "label": "Candlestick (OHLC)",
        "description": "Financial OHLC over time",
        "x": ["TEMPORAL"],
        "y": [],
        "color": [],
        "size": [],
        "requires_multiple_y": True,
        "min_numeric_for_corr": 0,
    },
    "choropleth": {
        "label": "Choropleth Map",
        "description": "Geographic regions colored by metric",
        "x": ["GEO"],
        "y": ["CONTINUOUS"],
        "color": [],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 0,
    },
    "parcoords": {
        "label": "Parallel Coordinates",
        "description": "Multivariate profiles (3–12 numeric columns)",
        "x": [],
        "y": [],
        "color": ["CONTINUOUS", "NONE"],
        "size": [],
        "requires_multiple_y": False,
        "min_numeric_for_corr": 3,
    },
}

AGGREGATE_FUNCTIONS = ["count", "mean", "median", "sum", "std", "min", "max"]
