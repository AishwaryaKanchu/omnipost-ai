"""Demo comparison: baseline generic AI vs OmniPost."""

COMPARE_DATA = {
    "label": "Demo evaluation data — not a live benchmark",
    "metrics": [
        {
            "name": "Voice Match (avg)",
            "baseline": 62,
            "omnipost": 89,
            "unit": "%",
        },
        {
            "name": "Unsupported claims",
            "baseline": 3,
            "omnipost": 0,
            "unit": "per run",
        },
        {
            "name": "Platform-specific angles",
            "baseline": 1,
            "omnipost": 3,
            "unit": "distinct",
        },
    ],
    "baseline_sample": (
        "Excited to share our new product! It's amazing and will change everything. "
        "Sign up today for great results. #innovation #business #growth"
    ),
    "omnipost_note": "Three native angles with voice scoring and fact checking.",
}
