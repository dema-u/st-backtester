# Trading algorithm based on ST-Patterns strategy

ST-Patterns algorithm implementation to trade on the FXCM exchange.

## Versioning

The repository and the trading bot follow the standard semantic versioning as major.minor.patch-release.

<ol>
<li><em>Major</em> - major release that fundamentally changes how the trading algorithm functions.</li>
<li><em>Minor</em> - minor release that signifies general improvements to the trading algorithm</li>
<li><em>Patch</em> - patch release that signifies a small bug or similar</li>
</ol>

All releases that are under development and are not ready to be allocated real capital will have a ```dev``` flag for release.

## Capital Allocation

To allocate capital to any given version of the algorithm the following criteria must be met.

<ol>
<li>The algorithm has been tested on the exchange for <strong>1 week</strong></li>
<li>The algorithm does not experience severe bugs during the test and manual intervention is rare (1-3 times in a week)</li>
<li>There were no fundamental structural changes in the market during the week i.e coronavirus</li>
</ol>