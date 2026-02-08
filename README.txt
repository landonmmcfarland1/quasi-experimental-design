# Quasi-Experimental Design: Universal Childcare and Maternal Employment

A replication and extension of Herbst (2017)'s study on the Lanham Act using difference-in-difference-in-differences (DiDiD) methodology. This project demonstrates proficiency in causal inference, quasi-experimental design, and econometric analysis by replicating a published *Journal of Labor Economics* article and extending it with novel research questions. For industry, this shows competency at being able to find causal effects when randomized control trials for governments or companies are impossible.

## Project Overview

This analysis replicates and extends **Study 1** of *"Universal Child Care, Maternal Employment, and Children's Long Run Outcomes"* by Chris M. Herbst (Journal of Labor Economics, 2017). The project uses a **triple-difference (DiDiD)** approach to estimate the causal effect of America's only universal childcare program—the Lanham Act (1943-1946)—on maternal labor supply.

### Research Context

During World War II, the U.S. federal government operated childcare centers to enable mothers to join the defense industry workforce. This created a natural experiment: mothers with young children (ages 0-12) gained access to affordable childcare, while women without qualifying children did not. Additionally, states varied dramatically in their spending levels, creating a second source of variation that strengthens causal identification.

### Novel Contribution

While Herbst (2017) focused on labor force entry (the **extensive margin**), this project extends the analysis to examine transitions within the labor force—specifically, whether childcare access enabled already-employed mothers to shift from part-time to full-time work (the **intensive margin**).

## Key Findings

### Replication Results (Herbst 2017)

**Employment Probability (Extensive Margin):**
- **DiDiD Coefficient**: 0.00214*** (p < 0.001)
- **Interpretation**: A $43 increase in per-child spending (25th→75th percentile) increased maternal employment by **9.2 percentage points**, representing a **58% increase** from the 1940 baseline

**Weekly Hours Worked:**
- **DiDiD Coefficient**: 0.09066*** (p < 0.001)
- **Interpretation**: The same spending increase raised hours worked by **3.9 hours per week**, a **69% increase** from pre-reform levels

### Extension Results (This Analysis)

**Part-Time Likelihood (Workers Only):**
- **DiDiD Coefficient**: -0.00069** (p < 0.01)
- **Interpretation**: Higher Lanham Act spending significantly reduced part-time work among employed mothers, facilitating transitions to full-time employment

**Hours Among Workers:**
- **DiDiD Coefficient**: 0.03145*** (p < 0.001)
- **Interpretation**: Even mothers already working increased their hours by **1.35 hours/week** in high-spending states

## Quick Start

This project uses [Pixi](https://pixi.sh/) for environment management and [Marimo](https://marimo.io/) for interactive Python notebooks.

### Installing Pixi

Pixi is a modern, cross-platform package manager that handles Python dependencies and virtual environments automatically.

**macOS/Linux:**
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

**Alternative (using Homebrew on macOS):**
```bash
brew install pixi
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS
```

### Running the Analysis

1. **Clone this repository** and navigate to the project directory

2. **Install dependencies**:
   ```bash
   pixi install
   ```

3. **Run the interactive notebook**:
   ```bash
   pixi run marimo edit didid-regression.py
   ```
   
   This will launch an interactive Marimo notebook in your web browser at `http://localhost:2718`

### Data Files

The dataset is **included in this repository**:
- `maternal_employment.dta` - Stata dataset with 1940 and 1950 U.S. Census data

**No additional downloads required!** The analysis runs immediately after `pixi install`.

## Project Structure

```
.
├── didid-regression.py            # Main Marimo notebook with full analysis
├── maternal_employment.dta.zip        # Census data (1940 & 1950)
├── pixi.toml                      # Pixi dependency configuration
├── pixi.lock                      # Locked dependency versions
└── README.md                      # This file
```

## Methodological Framework

### What is Difference-in-Differences (DiD)?

DiD estimates causal effects by comparing the change in outcomes for a treated group versus a control group before and after a policy intervention:

**Formula:**
```
Treatment Effect = (Treated After - Treated Before) - (Control After - Control Before)
```

**Key Assumption**: **Parallel Trends** - Without treatment, both groups would have followed the same trajectory over time.

### What is Difference-in-Difference-in-Differences (DiDiD)?

Standard DiD can be biased if other 1940s events differentially affected mothers versus non-mothers. DiDiD adds a **third difference**—variation in state-level spending—to strengthen causal identification.

**The DiDiD Question**: 
*"Did the employment gap between treated and control mothers grow more in high-spending states compared to low-spending states?"*

By interacting:
- **Treatment** (Mothers with young children vs. women without)
- **Time** (1940 vs. 1950)
- **Intensity** (State spending levels)

We isolate the causal effect of childcare access from confounding factors like regional economic shocks or general wartime mobilization.

### Why DiDiD Is More Credible Than DiD

**DiD vulnerability**: 
- What if high-spending states had booming defense industries that preferentially hired mothers?
- The DiD coefficient would conflate childcare effects with economic shocks

**DiDiD solution**: 
- By comparing *how the treatment-control gap changed differently across spending levels*, we difference out these state-specific shocks
- Only the interaction of all three factors (being a mother × post-1940 × high spending) drives the estimate

## Analysis Pipeline

### Step 1: Data Ingestion & Cleaning

**Source Data**: Integrated Public Use Microdata Series (IPUMS) 1940 and 1950 U.S. Census  
**Sample Restriction**: White, non-Hispanic women ages 25-64 (matching Herbst 2013)

**Data Preparation:**
```python
# Load Stata file
df = pd.read_stata('maternal_employment.dta', convert_categoricals=True)

# Filter to white mothers (Race != 2 drops Black mothers)
df = df[df['race'] != 2].copy()

# Handle missing values
df = df.replace('N/A', np.nan)

# Create part-time indicator (1-34 hours)
df['part_time'] = np.where((df['HRSWORK1'] >= 1) & (df['HRSWORK1'] <= 34), 1, 0)
```

### Step 2: Replication Regressions

**Model 1: Employment Probability (Binary Outcome)**

$$Y_{ist} = \beta_0 + \beta_1 \text{post}_t + \beta_2 \text{treated}_{ist} \times \text{post}_t + \beta_3 \text{treated}_{ist} \times \text{lanham}_s + \beta_4 \text{post}_t \times \text{lanham}_s + \beta_5 (\text{treated}_{ist} \times \text{post}_t \times \text{lanham}_s) + \alpha_i + \upsilon_s + \varepsilon_{ist}$$

**Model 2: Weekly Hours Worked (Continuous Outcome)**

Uses the same specification, but $Y_{ist}$ represents hours worked per week (0-98).

**Where:**
- $\beta_5$ = **DiDiD coefficient** (the causal effect we're estimating)
- $\text{treated}_{ist}$ = 1 if youngest child ages 0-12 during Lanham Act, 0 otherwise
- $\text{post}_t$ = 1 if year = 1950, 0 if year = 1940
- $\text{lanham}_s$ = State-level per-child spending (2012 dollars)
- $\alpha_i$ = Age fixed effects (40 categories)
- $\upsilon_s$ = State fixed effects (48 states)
- $\varepsilon_{ist}$ = Error term (clustered at state level)

**Implementation:**
```python
# Regression 1: Employment probability
model1 = smf.ols(
    'emp ~ treated*post1950*rlanham_012 + C(age) + C(statefip)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})

# Regression 2: Weekly hours
model2 = smf.ols(
    'HRSWORK1 ~ treated*post1950*rlanham_012 + C(age) + C(statefip)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})
```

### Step 3: Extension to Intensive Margin

**Model 3: Part-Time Probability (Workers Only)**

Restricts sample to employed mothers ($\text{emp} = 1$) and estimates:

$$\text{PartTime}_{ist} = \beta_0 + \beta_5 (\text{treated}_{ist} \times \text{post}_t \times \text{lanham}_s) + \text{controls} + \varepsilon_{ist}$$

**Model 4: Hours Among Workers**

Same specification as Model 2, but only for women with positive hours worked.

**Research Question**: 
*Did affordable childcare enable already-employed mothers to transition from part-time to full-time work?*

### Step 4: Visualization Strategy

Four panel plots showing **Lanham Act spending quartiles** (Q1 = lowest, Q4 = highest):

**Visual DiDiD Logic:**
1. Compare treated (blue) vs. control (red) lines within each quartile
2. Observe how the gap changes from 1940 → 1950
3. Check if gap expansion is larger in Q4 (high spending) vs. Q1 (low spending)

**If DiDiD effect exists:**
- Treated-control gap widens more in high-spending states
- Visualizations show diverging trends across spending quartiles

## Key Concepts Explained

### Parallel Trends Assumption

**Definition**: Without the Lanham Act, treated and control groups would have followed identical trajectories.

**How we test it**:
- Pre-1940 data would show parallel employment trends (not available in this dataset)
- State fixed effects absorb time-invariant differences
- Triple-difference framework differences out state-specific shocks

**Why it matters**: 
If violated, our coefficient estimates are biased. DiDiD is more robust than DiD because it requires parallel trends only *conditional on state spending levels*.

### Fixed Effects Strategy

**Age Fixed Effects ($\alpha_i$):**
- Controls for lifecycle employment patterns
- 40 categories (ages 25-64)
- Removes bias from age-related labor supply differences

**State Fixed Effects ($\upsilon_s$):**
- Absorbs time-invariant state characteristics
- Examples: cultural attitudes toward working mothers, baseline childcare availability
- Ensures we're not confusing California vs. Mississippi differences with treatment effects

### Clustered Standard Errors

**Why cluster at the state level?**
- Treatment (Lanham spending) varies at the state level
- Observations within states are not independent
- Standard OLS standard errors would be too small (overstate significance)

**Implementation:**
```python
.fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})
```

## Interpretation of Results

### Extensive Margin (Herbst Replication)

**DiDiD Coefficient (Employment): 0.00214***

**What it means:**
- A $1 increase in per-child spending raises employment probability by 0.214 percentage points
- Interquartile range effect (25th→75th percentile = $43 increase):
  - $43 × 0.00214 = **9.2 percentage point increase**
  - Relative to 1940 baseline (15.9%), this is a **58% increase**

**Policy interpretation**: 
States that invested heavily in the Lanham Act saw dramatically higher maternal employment rates by 1950, confirming that affordable childcare removes a binding constraint on labor supply.

### Intensive Margin (Extension)

**DiDiD Coefficient (Part-Time): -0.00069**

**What it means:**
- Higher spending reduced part-time work likelihood among employed mothers
- The Lanham Act didn't just get mothers into the labor force—it enabled full-time work

**Why this matters**: 
Part-time work often lacks benefits, career advancement, and wage premiums. The finding that childcare access facilitates full-time employment has important implications for gender wage gaps and long-term career trajectories.

## Limitations and Scope

### Simplified Specification

**Controls NOT included** (but used in Herbst 2013):
- Marital status (6 dummies)
- Educational attainment (21 dummies)
- U.S.-born indicator
- Metropolitan residence (4 dummies)

**Why simpler?**
- Demonstrates core DiDiD mechanism without demographic controls
- Clearer interpretation of triple-interaction term
- State and age fixed effects absorb major confounders

**Trade-off**: 
Our coefficients show larger magnitudes than the original paper but are directionally consistent.

### Data Constraints

**What we have:**
- Two time points (1940, 1950)
- Cross-sectional data (cannot track same individuals over time)
- State-level spending variation only

**What we don't have:**
- Pre-1940 data to formally test parallel trends
- Individual-level childcare usage
- Quality metrics for Lanham Act centers

## Technologies

### Core Stack

- **Python 3.14**: Latest Python release
- **Marimo**: Reactive notebooks for reproducible analysis
- **Pandas**: Data manipulation and analysis
- **Statsmodels**: Econometric regression with clustered standard errors
- **Seaborn + Matplotlib**: Statistical visualization
- **Pixi**: Cross-platform package manager

### Why This Stack?

**Marimo for Reproducibility:**
- Pure Python files (`.py` not `.ipynb`)
- Reactive execution ensures consistency
- No hidden state issues
- Version control friendly

**Statsmodels for Econometrics:**
- Industry-standard for causal inference
- Clustered standard errors essential for DiDiD
- Formula API matches R/Stata syntax
- Robust covariance matrix estimators

**Seaborn for Visualization:**
- FacetGrid for multi-panel DiDiD plots
- Point plots with confidence intervals
- Publication-quality output

## Policy Implications

### What the Lanham Act Achieved

1. **Massive labor supply response**: 9.2pp employment increase from affordable childcare
2. **Dose-response relationship**: More spending → bigger effects
3. **Persistent effects**: Changes visible 5 years post-program
4. **Both margins**: Increased entry (extensive) AND work hours (intensive)

### Modern Relevance

**Why this matters today:**
- U.S. childcare costs average $10,000-$20,000/year (30-50% of median income)
- Female labor force participation has stalled since 2000
- The Lanham Act shows universal childcare can fundamentally reshape labor markets

**What's different in 2026:**
- Dual-earner norms stronger than 1940s
- Service economy vs. manufacturing
- Remote work options
- Higher educational attainment among women

## Replication Instructions

### Running the Full Analysis

After `pixi run marimo edit didid-regression.py`:

1. **Read conceptual overview** (Cells 1-4)
2. **Load and clean data** (Cells 5-6)
3. **Run replication regressions** (Cells 7-8)
4. **Run extension regressions** (Cells 9-10)
5. **Generate visualizations** (Cell 11)
6. **Interpret results** (Cells 12-13)

### Modifying the Analysis

**To add controls:**
```python
# Add education controls to Model 1
model1 = smf.ols(
    'emp ~ treated*post1950*rlanham_012 + C(age) + C(statefip) + C(education)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})
```

**To test different spending measures:**
```python
# Use categorical spending bins instead of continuous
df['spending_category'] = pd.qcut(df['rlanham_012'], q=3, labels=['Low', 'Med', 'High'])
model_categorical = smf.ols(
    'emp ~ treated*post1950*C(spending_category) + C(age) + C(statefip)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})
```

**To examine heterogeneous effects:**
```python
# Interaction with marital status
model_married = smf.ols(
    'emp ~ treated*post1950*rlanham_012*C(marital_status) + C(age) + C(statefip)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['statefip']})
```

## Academic Context

**Original Paper**: Herbst, C. M. (2017). Universal Child Care, Maternal Employment, and Children's Long-Run Outcomes: Evidence from the US Lanham Act of 1940. *Journal of Labor Economics*, 35(2), 519-564.

**Methodology**: Quasi-experimental design (DiDiD)  
**Data Source**: IPUMS USA (Integrated Public Use Microdata Series)  
**Historical Context**: World War II defense mobilization, 1943-1946  

**Learning Objectives Demonstrated**:
- Causal inference with observational data
- Triple-difference estimation strategy
- Fixed effects regression modeling
- Clustered standard error calculation
- Parallel trends assumption evaluation
- Economic policy analysis

## License

This project is available for educational purposes. Data is from IPUMS USA and subject to their terms of use.

## Data Source Attribution

**Original Study**: Herbst (2017), *Journal of Labor Economics*  
**Data Source**: IPUMS USA (University of Minnesota)  
**Historical Program**: Lanham Act (1943-1946), U.S. Federal Works Agency

## Acknowledgments

- **Chris M. Herbst** for the original research design and data preparation
- **IPUMS USA** for providing harmonized census microdata
- **Marimo and Statsmodels** development communities

---

**Questions or Issues?**

If you encounter any problems replicating this analysis or have questions about the quasi-experimental methodology, please open an issue on GitHub.
