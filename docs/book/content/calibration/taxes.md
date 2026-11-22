(Chap_Taxes)=
# Taxes

Japan has no open-source tax microsimulation model (no equivalent of the US [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator)), so `OG-JPN` cannot estimate OG-Core's nonlinear tax functions from microdata the way OG-USA does. Instead it uses OG-Core's **linear** tax functions, with each rate taken from a published source (`ogjpn/tax_params.py`). That gives no more precision than the data support.

| Tax | Model rate | Source |
|---|---|---|
| Personal income, average effective (`etr_params`) | 8% | OECD *Taxing Wages 2025*: 22.0% net average rate for a single worker at the average wage, of which ~15 points is employee social insurance |
| Labor income, marginal (`mtrx_params`) | 30% | 20% national band + 10% local inhabitant tax (PwC Worldwide Tax Summaries) |
| Capital income, marginal (`mtry_params`) | 20.315% | 15% national + 5% local + 0.315% reconstruction surtax on dividends, interest, and listed capital gains |
| Social insurance (`tau_payroll`) | 30% | pension 18.3% + health ~10% + long-term care ~0.8% (blended) + employment ~0.9%; employer and employee shares, both borne by labor (Japan Pension Service, MHLW) |
| Corporate income (`cit_rate`) | 30% | national 23.2% plus local corporate, inhabitant, and enterprise taxes (PwC, JETRO) |
| Consumption (`tau_c`) | 10% | standard rate since October 2019 (National Tax Agency) |

## A US tax system cannot fund a Japanese government

With OG-Core's default US tax functions and Japan's debt target, the government budget only closed with **negative** government purchases. Replacing them with Japan's actual rates, mainly the 30 percent social insurance contribution, raises revenue to about 32 percent of GDP and closes the budget with positive purchases. The tax side, not only the demographics, now belongs to Japan.

## Known limitations

* **No progressivity.** The income tax is a single average effective rate with a constant marginal rate, not Japan's seven-bracket schedule (5 to 45 percent). Fitting a progressive function needs the income distribution behind the published effective rates.
* **No contribution cap.** Social insurance contributions in Japan are capped at a maximum standard remuneration. The cap is not modeled, which overstates the rate for high earners.
* **Revenue gap.** Model revenue is about 32 percent of GDP against Japan's 37.6 percent (IMF). Japan's property tax (Fixed Asset and City Planning Tax, about 2 percent of GDP) can be added through OG-Core's wealth tax and raises revenue to about 34 percent, but it makes the consumption-tax reform fail to converge, so it is deferred. Inheritance and other minor taxes make up the rest.
