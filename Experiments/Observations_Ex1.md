# Experiment 1 — Balance Profiling: Results & Observations

## Output
- Louvain detected **40 communities**
- Only **5 communities** had a computable balance score (i.e. contained closed triangles)
- Mean balance score: **0.627** | Median: **0.767**

## Observations

### 1. Most communities are too small for balance scoring
35 out of 40 communities contained no closed triangles, making balance scoring impossible.
This is a direct consequence of Louvain's resolution limit — it fragments the network into many
tiny communities (often 2-3 nodes) with no internal triadic structure.
**Fix:** apply a minimum size threshold (e.g. drop communities < 50 nodes) before balance scoring.

### 2. Community 5 (size=2) should be ignored
A balance score of 0.0 on a 2-node community is meaningless — it has one positive and one
negative edge with no triangle possible. This is an artifact of Louvain over-fragmenting, not
a real finding.

### 3. Balance theory holds empirically
All four meaningful communities score well above the random baseline of 0.5 (range: 0.748–0.827).
This confirms that communities are more internally balanced than chance would predict — people in
the same community tend to share consistent trust/distrust patterns, consistent with balance theory.

### 4. Variation between communities is meaningful
| Community | Size | Balance Score | Interpretation |
|-----------|------|---------------|----------------|
| 4 | 1709 | 0.748 | Most internally tense |
| 6 | 2871 | 0.767 | Largest, moderate tension |
| 0 | 776  | 0.789 | Mid stability |
| 1 | 1652 | 0.827 | Most stable |

Community 4 is the most tense despite being large — the primary candidate for Experiment 3
(fragmentation test).

### 5. Negative edges are evenly distributed across communities
The negative edge ratio within each community (~20–25%) mirrors the global ratio of ~21%.
Negative edges are not concentrated in specific communities — they are spread evenly across
the network. This suggests fragmentation effects may be subtle rather than driven by a few
highly toxic communities.

## Limitations
- Only 5/40 communities were usable — triadic structure is too sparse in most communities
- Louvain's resolution limit likely over-fragments the network; consider re-running with a
  minimum size filter or trying the Leiden algorithm as a more stable alternative
- Balance scores cannot be computed for isolated or near-isolated communities, which biases
  results toward large, dense communities only