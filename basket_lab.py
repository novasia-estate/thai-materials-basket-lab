# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo>=0.18"]
# ///
import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import csv
    import io
    import marimo as mo
    return csv, io, mo


@app.cell
def _():
    # TPSO, October 2026 CMI release, final statistical table, 2021 = 100.
    data = (
        ("Wood products", 3.03, 123.2, 118.0, 4.4, 4.3, 2.6),
        ("Cement", 12.12, 113.9, 114.5, -0.5, 0.3, 2.1),
        ("Concrete products", 17.86, 119.6, 109.2, 9.5, 9.2, 6.8),
        ("Steel products", 23.24, 99.2, 99.3, -0.1, -0.8, 1.0),
        ("Tiles", 6.32, 109.5, 103.1, 6.2, 4.0, 2.4),
        ("Surface finishes", 2.71, 109.9, 106.2, 3.5, 2.2, 0.9),
        ("Sanitary ware", 3.10, 99.0, 93.5, 5.9, 4.8, 1.0),
        ("Electrical and plumbing", 15.44, 124.1, 109.4, 13.4, 13.3, 9.1),
        ("Other materials", 16.17, 132.2, 108.5, 21.8, 19.8, 11.2),
    )
    baskets = {
        "Concrete-led shell": (3, 15, 42, 29, 0, 1, 0, 5, 5),
        "Fit-out package": (12, 3, 5, 3, 18, 12, 13, 29, 5),
        "Services-heavy package": (2, 5, 12, 12, 3, 4, 4, 48, 10),
    }
    periods = {
        "October 2026 vs October 2025": (4, 7.4),
        "September 2026 vs September 2025": (5, 6.8),
        "Jan–Oct 2026 vs Jan–Oct 2025 averages": (6, 4.9),
    }
    return baskets, data, periods


@app.cell
def _(mo):
    mo.md("""
    # When the materials index and the basket diverge

    **Thailand · Construction Materials Price Index · October 2026 release**

    Pick a comparison period and three hypothetical procurement mixes. Then vary the
    exposure to concrete and building services without changing the scale of the basket.
    The output shows the contribution of each category in percentage points.

    Research notebook by [NovAsia Estate](https://novasia.estate/).
    """)
    return


@app.cell
def _(baskets, mo, periods):
    period = mo.ui.dropdown(options=list(periods), value=next(iter(periods)), label="Comparison period")
    chosen = mo.ui.dropdown(options=list(baskets), value=next(iter(baskets)), label="Basket to inspect")
    concrete = mo.ui.slider(0, 80, value=42, step=1, show_value=True, label="Custom concrete weight units")
    installations = mo.ui.slider(0, 80, value=5, step=1, show_value=True, label="Custom electrical/plumbing units")
    mo.vstack([mo.hstack([period, chosen], wrap=True), mo.hstack([concrete, installations], wrap=True)])
    return chosen, concrete, installations, period


@app.cell
def _():
    def contribution(weights, changes):
        total = sum(weights)
        if total <= 0:
            raise ValueError("Total weight must be positive")
        shares = [weight / total for weight in weights]
        return [(share, share * rate) for share, rate in zip(shares, changes, strict=True)]
    return (contribution,)


@app.cell
def _(baskets, chosen, concrete, contribution, data, installations, period, periods):
    rate_column, official = periods[period.value]
    changes = [row[rate_column] for row in data]
    weight_sets = dict(baskets)
    base = list(baskets[chosen.value])
    base[2], base[7] = concrete.value, installations.value
    weight_sets["Custom mix"] = tuple(base)
    cases = {name: contribution(weights, changes) for name, weights in weight_sets.items()}
    totals = {name: sum(value for _, value in parts) for name, parts in cases.items()}
    return cases, changes, official, totals


@app.cell
def _(mo, official, totals):
    rows = "\n".join(
        f"| {name} | {value:+.2f}% | {value-official:+.2f} pp |"
        for name, value in totals.items()
    )
    mo.md("## Compare four mixes\n\n"
          "| Scenario | Modelled change | Difference from published CMI |\n"
          "|:--|--:|--:|\n"
          f"| Published national CMI | {official:+.1f}% | Reference |\n" + rows)
    return


@app.cell
def _(cases, changes, chosen, data, mo):
    result = []
    for (label, *_), change, (share, value), (custom_share, custom_value) in zip(
        data, changes, cases[chosen.value], cases["Custom mix"], strict=True
    ):
        result.append({"Category": label, "Published change (%)": change,
                       "Preset share (%)": round(share * 100, 2),
                       "Preset contribution (pp)": round(value, 2),
                       "Custom share (%)": round(custom_share * 100, 2),
                       "Custom contribution (pp)": round(custom_value, 2)})
    mo.vstack([mo.md("## Where the difference comes from"), mo.ui.table(result, pagination=False, selection=None)])
    return (result,)


@app.cell
def _(csv, io, mo, result):
    destination = io.StringIO()
    writer = csv.DictWriter(destination, fieldnames=list(result[0]))
    writer.writeheader()
    writer.writerows(result)
    mo.download(destination.getvalue().encode("utf-8"), filename="material-basket-contributions.csv", label="Download contributions as CSV")
    return


@app.cell
def _(data, mo):
    mo.accordion({"Official input values": mo.ui.table([
        {"Material": label, "Official weight (%)": weight, "Oct 2026 index": current,
         "Oct 2025 index": previous, "Oct YoY (%)": oct_rate,
         "Sep YoY (%)": sep_rate, "Jan–Oct average change (%)": average}
        for label, weight, current, previous, oct_rate, sep_rate, average in data
    ], pagination=False, selection=None)})
    return


@app.cell
def _(mo):
    mo.md("""
    ## Calculation and interpretation

    Each row contributes its normalised base-period cost share times the published
    percentage change for its material category. Summing signed contributions gives
    the change of the modelled materials basket. Setting two category weights to zero
    distributes the remaining share across the other categories.

    The official index is shown as a separately published reference. It covers materials
    traded in 20 provinces; the scenario weights are illustrative. Use quantities,
    supplier quotes, labour, tax, lead times and a defined contract price date for an
    actual cost estimate. The year-to-date comparison uses the publisher's two period
    averages. It is a separate lens from the October and September point comparisons.

    [TPSO October 2026 release and statistical table](https://uploads.tpso.go.th/editor/pdf/1793934481_51742b5d42193db36f37.pdf) ·
    [CMI data portal](https://index.tpso.go.th/materials-price-index)
    """)
    return


if __name__ == "__main__":
    app.run()
