"""
Interactive Coin Flip Simulator with CLT Verification
Drag the slider to change the number of flips.
One simulation = one full set of n flips. The result is a single head count.
Requirements: pip install numpy matplotlib scipy
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
from scipy import stats


P_HEADS = 0.5

# Store current simulation
current = {"flips": None, "n_flips": 0, "heads": 0}


def run_simulation(n_flips):
    """Flip n_flips coins. Store each individual flip and total heads."""
    flips = np.random.choice([0, 1], size=n_flips, p=[1 - P_HEADS, P_HEADS])
    heads = int(flips.sum())
    current["flips"] = flips
    current["n_flips"] = n_flips
    current["heads"] = heads
    return flips, heads


def setup_plot():
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(11, 8),
                                          gridspec_kw={"height_ratios": [2, 1]})
    plt.subplots_adjust(bottom=0.25, hspace=0.35)

    n_flips_init = 1000

    # --- Slider ---
    slider_ax = plt.axes([0.15, 0.10, 0.55, 0.03])
    slider = Slider(slider_ax, "Flips", 10, 50000, valinit=n_flips_init,
                    valstep=10, color="steelblue")

    # --- Text box ---
    query_ax = plt.axes([0.15, 0.03, 0.15, 0.04])
    text_box = TextBox(query_ax, "Check heads = ", initial="")

    prob_text = fig.text(0.35, 0.04, "", fontsize=10,
                         bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    # --- Re-roll button ---
    button_ax = plt.axes([0.78, 0.10, 0.12, 0.04])
    button = Button(button_ax, "Re-roll", color="lightgray", hovercolor="lightblue")

    def update(val=None):
        n_flips = int(slider.val)
        flips, heads = run_simulation(n_flips)
        mu = n_flips * P_HEADS
        sigma = np.sqrt(n_flips * P_HEADS * (1 - P_HEADS))

        # -- Top plot: running cumulative proportion of heads --
        ax_top.cla()
        cumulative = np.cumsum(flips) / np.arange(1, n_flips + 1)
        # Downsample for performance if many flips
        step = max(1, n_flips // 2000)
        ax_top.plot(np.arange(1, n_flips + 1, step), cumulative[::step],
                    color="steelblue", lw=1)
        ax_top.axhline(P_HEADS, color="red", linestyle="--", lw=1.5, label=f"Expected = {P_HEADS}")
        ax_top.set_xlabel("Flip number")
        ax_top.set_ylabel("Cumulative proportion of heads")
        ax_top.set_title(f"{n_flips:,} coin flips  —  Result: {heads:,} heads "
                         f"({heads/n_flips:.2%})", fontsize=13)
        ax_top.legend(loc="upper right")
        ax_top.set_ylim(0.3, 0.7)

        # -- Bottom plot: where this result falls on the CLT distribution --
        ax_bot.cla()
        x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 300)
        ax_bot.plot(x, stats.norm.pdf(x, mu, sigma), "r-", lw=2, label="CLT Normal")
        ax_bot.fill_between(x, stats.norm.pdf(x, mu, sigma), alpha=0.15, color="red")
        ax_bot.axvline(heads, color="green", linestyle="--", lw=2,
                       label=f"Your result: {heads:,}")
        ax_bot.set_xlabel("Number of Heads")
        ax_bot.set_ylabel("Density")
        ax_bot.set_title(f"CLT distribution  (mu={mu:.0f}, sigma={sigma:.1f})", fontsize=12)
        ax_bot.legend(loc="upper right")

        prob_text.set_text("")
        fig.canvas.draw_idle()

    def on_submit(text):
        try:
            x = int(text)
            n_flips = current["n_flips"]
            heads = current["heads"]
            mu = n_flips * P_HEADS
            sigma = np.sqrt(n_flips * P_HEADS * (1 - P_HEADS))

            # CLT probabilities
            clt_exact = (stats.norm.cdf(x + 0.5, mu, sigma)
                         - stats.norm.cdf(x - 0.5, mu, sigma))
            clt_ge = 1 - stats.norm.cdf(x - 0.5, mu, sigma)

            got_it = "YES" if heads == x else "NO"
            diff = heads - x

            prob_text.set_text(
                f"You got {heads:,} heads.  Exactly {x}? {got_it} (off by {diff:+d})  |  "
                f"CLT: P(={x}) = {clt_exact:.4%},  P(>={x}) = {clt_ge:.4%}")

            # Mark on bottom plot
            ax_bot.axvline(x, color="orange", linestyle=":", lw=2, label=f"Query: {x:,}")
            ax_bot.legend(loc="upper right")
            fig.canvas.draw_idle()

        except ValueError:
            prob_text.set_text("Enter a valid integer")
            fig.canvas.draw_idle()

    slider.on_changed(update)
    button.on_clicked(update)
    text_box.on_submit(on_submit)

    update()
    plt.show()


if __name__ == "__main__":
    setup_plot()
