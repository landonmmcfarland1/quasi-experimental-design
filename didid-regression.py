import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import statsmodels.formula.api as smf
    import pyarrow as pa
    import seaborn as sns
    import matplotlib.pyplot as plt

    return mo, np, pd, plt, smf, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Project Overview: Quasi-experimental Design

    - Project replicates and extends study 1 of **"Universal Child Care, Maternal Employment, and Children's Long Run Outcomes"** published by Chris M. Herbst in the *Journal of Labor Economics*, using a **difference-in-difference-in-differences (DiDiD)** approach.
    - This analysis extends the original research to investigate how government policy influenced mothers' transition from part-time to full-time employment for mothers already in the labor force in 1940.
    - The project goes as follows:
      - **Defining the importance of quasi-experiments**
      - **Defining Difference-in-differences (DiD)**
      - **Defining Difference-in-differences-in-differences (DiDiD)**
      - **Step 1: Data Ingestion using Pandas**
      - **Step 2: Replication Regressions**
      - **Step 3: Extending the Model to Internal Labor Transitions**
      - **Step 4: Comparison of Original Paper and New Contributions**
      - **Step 5: DiDiD Quasi-experiment Visualizations**
      - **Step 6: DiDiD Coefficient & Visualization Interpretations**
      - **Step 6: Overall Conclusions**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**What can Quasi-experiments do?**
    - Many industries struggle to understand the effectiveness of actions when "clean" randomized experiments cannot occur. For example...
      - Stores cannot charge different prices to the different customers in the same store without causing brand damage
      - A logistics company cannot "turn off" a routing software for specific vans without disrupting the workflow of a facility
    - However, they can compare two groups whose outcomes were trending in the same direction at the beginning of data collection and find the true impact by calculating: (Group A Change) minus (Group B Change).
    - Going back to our examples, if a logistics company had two locations with comparable increasing revenue over time, you can find the "true impact" of a new routing system for "location A" by solving:
      - True Impact of Routing System = ((Location A Revenue After - Location A Revenue Before) - (Location B Revenue After - Location B Revenue Before))
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**What is a Difference-in-Differences approach?**

    - A difference-in-differences regression approach attempts to assess the change in outcomes for a group before and after a policy or market/company action by comparing that group to the change in the control group during the same period.
    - Difference-in-differences relies on **THE PARALLEL TRENDS ASSUMPTION.** The validity of this approach says that the control group and the treated group would have followed the same trajectory over time if no treatment were to occur
    - By using this approach, we assume that the employment rates and average hours worked weekly for mothers who would eventually and would not eventually qualify for the Lanham Act's childcare would have followed the same trajectory (i.e., their regression coefficients have parallel trends).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**What is a Difference-in-Difference-in-Differences approach?**

    - A standard DiD model might still be biased if there were other events in the 1940s that only affected mothers whose children qualified for universal childcare programs. To solve this, the original paper utilizes a Triple-Difference model, which adds a third layer of comparison: State-level spending.
    - The DiDiD model attempts to explain "Did the gap between individuals who had kids who qualified for the Lanham Act vs those whose kids didn't qualify grow more significantly in states that received high levels of Lanham ACt funding comapred to states with low funding?"
    - By interacting Treatment (Mothers), Time (Post-1940s), and Intensity (State Spending), the model provides us a higher level of confidence that the observed changes in labor supply and average hours working a week were actually CAUSED by the childcare program and not due to regional economic shifts or general war mobilization in 1940s United States.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Step 1: Data Ingestion**

    - To ensure the integrity of the replication, this step attempts to match the Python environment with the original Stata-based methodology used by Herbst.

      - Demographic Focus: The sample is restricted to white, non-Hispanic women in their prime working years (ages 25–64).

      - Categorical Handling: I converted the original .dta file, ensuring that placeholders like 'N/A' are converted to computational NaNs for accurate regression modeling.

      - Feature Engineering: I generated the primary part_time indicator (1–34 hours)
    """)
    return


@app.cell
def _(np, pd):
    #1. Load the data
    df = pd.read_stata('maternal_employment.dta', convert_categoricals=True)


    #2. Filter: Keep only White mothers (Race != 2 means dropping Black mothers)
    # This matches line 12 of your original Stata do-file
    df = df[df['race'] != 2].copy()

    #3. Clean Missing Values: Replace 'N/A' strings with actual NaNs
    df = df.replace('N/A', np.nan)

    #4. Verify the data loaded
    print(f"Data loaded successfully: {len(df)} observations ready for analysis.")
    df.head(10)
    return (df,)


@app.cell
def _(df, np, pd):
    df['HRSWORK1'] = pd.to_numeric(df['HRSWORK1'], errors='coerce')

    #Part-Time Likelihood: 1 if 1-34 hours, 0 if 35+ hours
    #We only calculate this for workers in the next step
    df['part_time'] = np.where((df['HRSWORK1'] >= 1) & (df['HRSWORK1'] <= 34), 1, 0)


    #Categorize states based on the 'rlanham_012' column identified in file
    median_val = df['rlanham_012'].median()
    df['high_lanham'] = np.where(df['rlanham_012'] > median_val, 'High Spending', 'Low Spending')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Step 2: Replication Regressions**

    ## **Mathematical Framework: DiDiD Replication Regression Models**

    ## **Regression Specifications Used in This Analysis**

    ### **Models 1 & 2: Replication of Herbst (2013) - All Mothers**

    $$Y_{ist} = \beta_0 + \beta_1 \text{post}_t + \beta_2 \text{treated}_{ist} \times \text{post}_t + \beta_3 \text{treated}_{ist} \times \text{lanham}_s + \beta_4 \text{post}_t \times \text{lanham}_s + \beta_5 (\text{treated}_{ist} \times \text{post}_t \times \text{lanham}_s) + \alpha_i + \upsilon_s + \mu_{ist}$$

    Where:
    * $Y_{ist}$: Outcome for woman $i$ in state $s$ at time $t$
      - **Model 1**: Employment likelihood (binary: 1 if employed, 0 otherwise)
      - **Model 2**: Weekly hours worked (continuous: 0-98 hours)
    * $\beta_5$: **DiDiD coefficient** - the causal effect of the Lanham Act
    * $\text{treated}_{ist}$: Binary indicator (1 if youngest child ages 0-12 during Lanham Act, 0 otherwise)
    * $\text{post}_t$: Binary indicator (1 if year = 1950, 0 if year = 1940)
    * $\text{lanham}_s$: Continuous measure of state-level Lanham Act spending per child ages 0-12 (in 2012 dollars)
    * $\alpha_i$: **Age fixed effects** - controls for 40 age categories (25-64)
    * $\upsilon_s$: **State fixed effects** - controls for unobserved state characteristics (48 states)
    * $\mu_{ist}$: Error term, clustered at the state level

    ---

    ### **Key Differences from Original Paper**

    **Controls NOT included in our specification** (but used in Herbst 2013):
    - Marital status (6 dummy variables)
    - Educational attainment (21 dummy variables)
    - U.S. born indicator
    - Metropolitan residence (4 dummy variables)

    **Why the simpler specification?**
    Our analysis uses the **minimal DiDiD framework** with only fixed effects to establish the core causal mechanism. This approach:
    1. Demonstrates the treatment effect without demographic controls
    2. Allows for clearer interpretation of the triple-interaction term
    3. Relies on state and age fixed effects to control for major confounders

    The original paper's full specification with demographic controls produces similar directional results but with different magnitudes.

    ---

    ### **Research Hypotheses**

    **Herbst (2013) Replication:**
    * **H1**: Universal childcare increases maternal labor force participation ($\beta_5 > 0$ in Model 1)
    * **H2**: Universal childcare increases total work hours for all mothers ($\beta_5 > 0$ in Model 2)

    **McFarland Extension:**
    * **H3**: Universal childcare enables part-time workers to transition to full-time employment ($\beta_5 < 0$ in Model 3)
    * **H4**: Universal childcare increases work intensity for already-employed mothers ($\beta_5 > 0$ in Model 4)
    """)
    return


@app.cell
def _(df, smf):
    df['treat_post_cont'] = df['treated'] * df['post']
    df['treat_lanham_cont'] = df['treated'] * df['rlanham_012']
    df['post_lanham_cont'] = df['post'] * df['rlanham_012']
    df['ddd_cont'] = df['treated'] * df['post'] * df['rlanham_012']

    # Formula using continuous lanham variable with fixed effects
    formula = "rlanham_012 + post + treat_post_cont + treat_lanham_cont + post_lanham_cont + ddd_cont + C(statefip) + C(age)"

    # Regression 1: Likelihood of being employed (Extensive Margin)
    model_paper_emp = smf.ols(f"emp ~ {formula}", data=df).fit(
        cov_type='cluster', cov_kwds={'groups': df['statefip']}
    )

    # Regression 2: Number of hours worked (Intensive Margin - Unconditional)
    model_paper_hours = smf.ols(f"HRSWORK1 ~ {formula}", data=df).fit(
        cov_type='cluster', cov_kwds={'groups': df['statefip']}
    )

    print("Original Paper Replication Complete.")
    return formula, model_paper_emp, model_paper_hours


@app.cell
def _(model_paper_emp):
    print("Regression 1 - Original Paper's DiDiD Treatment Effect onto Employment Likelihood")
    print()
    print(model_paper_emp.summary())
    return


@app.cell
def _(model_paper_hours):
    print('Regression 2 - DiDiD Effect onto Number of Weekly Hours Working')
    print()
    print(model_paper_hours.summary())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Step 3: Extending the Model to Internal Labor Transitions**

    While the original study focuses on the **Extensive Margin** (entering the workforce), this section investigates the **Conditional Intensive Margin**. We examine how the Lanham Act influenced behavior for mothers who were **already employed**.

    ### **Models 3 & 4: McFarland Extension - Already-Employed Mothers Only**

    $$Y_{ist} = \beta_0 + \beta_1 \text{post}_t + \beta_2 \text{treated}_{ist} \times \text{post}_t + \beta_3 \text{treated}_{ist} \times \text{lanham}_s + \beta_4 \text{post}_t \times \text{lanham}_s + \beta_5 (\text{treated}_{ist} \times \text{post}_t \times \text{lanham}_s) + \alpha_i + \upsilon_s + \mu_{ist}$$

    **Sample restriction**: $\text{emp}_{ist} = 1$ (only women employed in the reference week)

    Where:
    * $Y_{ist}$: Outcome for **employed** woman $i$ in state $s$ at time $t$
      - **Model 3**: Part-time employment likelihood (binary: 1 if 1-34 hours/week, 0 if 35+ hours)
      - **Model 4**: Weekly hours worked (continuous: 1-98 hours, conditional on employment)
    * All other variables defined identically to Models 1 & 2


     **Interpretation of the DiDiD Coefficient ($\beta_5$)**

    The DiDiD estimator answers: **"How much more did mothers in high-spending states increase their labor supply after the Lanham Act, compared to mothers in low-spending states?"**

    **For a $1 increase in per-child Lanham spending:**
    - Employment probability increases by $\beta_5$ percentage points
    - Weekly hours worked increases by $\beta_5$ hours
    """)
    return


@app.cell(hide_code=True)
def _(df, formula, smf):
    #1. Filter to mothers WHO ARE ALREADY EMPLOYED 
    df_workers = df[df['emp'] == 1].copy()

    #2. Run the same DiDiD model as before, but on the CONDITIONAL sample
    model_my_pt = smf.ols(f"part_time ~ {formula}", data=df_workers).fit(
        cov_type='cluster', cov_kwds={'groups': df_workers['statefip']}
    )

    model_my_hours = smf.ols(f"HRSWORK1 ~ {formula}", data=df_workers).fit(
        cov_type='cluster', cov_kwds={'groups': df_workers['statefip']}
    )

    print("Extension Analysis (Employed Mothers Only) Complete.")
    return model_my_hours, model_my_pt


@app.cell
def _(model_my_pt):
    print('McFarland Regression 1 - DiDiD Treatment Effect onto Part-Time Employment Status for Already Employed Mothers')
    print(model_my_pt.summary())
    return


@app.cell
def _(model_my_hours):
    print('McFarland Regression 2 - DiDiD Treatment Effect onto Avg. Weekly Hours Worked for Already Employed Mothers')
    print(model_my_hours.summary())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**Step 4: Comparison of Original Paper and New Contributions**
    """)
    return


@app.cell(hide_code=True)
def _(model_my_hours, model_my_pt, model_paper_emp, model_paper_hours):
    from statsmodels.iolib.summary2 import summary_col

    # 1. Group your 4 models into a list
    models = [model_paper_emp, model_paper_hours, model_my_pt, model_my_hours]

    # 2. Define column names for the table
    col_names = ['1', '2', '3', '4']

    # 3. Create the table
    # 'stars=True' adds the academic significance markers (*** p<0.01)
    # 'regressor_order' puts your main DDD variable at the top
    # 'info_dict' adds extra rows like Number of Observations at the bottom
    df_summary = summary_col(
        models, 
        stars=True, 
        float_format='%0.5f',
        model_names=col_names,
        regressor_order=['ddd_cont', 'post', 'treated'], # Focus on these key variables
        drop_omitted=True # This hides the hundreds of State/Age fixed effect rows
    )

    # 4. Final Formatting
    df_summary.add_title('Table Comparison: Original Paper Replication & Original Contributions')
    print(df_summary)
    print('Column 1 - Original paper results for employment likelihood for mothers.')
    print('Column 2 - Original paper results for avg. weekly hrs worked for mothers.')
    print('Column 3 - My results for part-time employment likelihood for mothers already employed in 1940.')
    print('Column 4 - My results for avg. weekly hrs worked for mothers already employed in 1940.')
    print('DDD = interaction of Treated (Child qualified for care vs Not) X Post (Before & After) X (Lanham (High vs Low state level spending for childcare)')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**Step 5: DiDiD Quasi-experiment Visualizations**
    """)
    return


@app.cell(hide_code=True)
def _(df, np, pd, plt, sns):
    # 1. Prepare visualization dataset
    viz_df = df.copy()
    viz_df['Period'] = np.where(viz_df['post'] == 1, '1950 (Post)', '1940 (Pre)')
    viz_df['Group'] = np.where(viz_df['treated'] == 1, 'Treated (Mothers)', 'Control')

    # 2. Create spending quartiles using pd.cut - MUCH SIMPLER
    viz_df['lanham_quartile'] = pd.qcut(
        viz_df['rlanham_012'], 
        q=4, 
        labels=['Q1: Low Spending', 'Q2: Medium-Low', 'Q3: Medium-High', 'Q4: High Spending']
    )

    # REGRESSION 1: Employment Probability
    g1 = sns.catplot(
        data=viz_df, 
        x='Period', 
        y='emp', 
        hue='Group', 
        col='lanham_quartile',
        kind='point', 
        capsize=0.1, 
        palette='Set1', 
        height=4, 
        aspect=0.8
    )
    g1.fig.suptitle('DiDiD: Employment Probability by Lanham Spending Quartile', y=1.02)

    # REGRESSION 2: Weekly Hours
    g2 = sns.catplot(
        data=viz_df, 
        x='Period', 
        y='HRSWORK1', 
        hue='Group', 
        col='lanham_quartile',
        kind='point', 
        capsize=0.1, 
        palette='Set1', 
        height=4, 
        aspect=0.8
    )
    g2.fig.suptitle('DiDiD: Weekly Hours by Lanham Spending Quartile', y=1.02)

    # Workers only
    worker_viz_df = viz_df[viz_df['emp'] == 1].copy()

    # REGRESSION 3: Part-Time Probability
    g3 = sns.catplot(
        data=worker_viz_df, 
        x='Period', 
        y='part_time', 
        hue='Group', 
        col='lanham_quartile',
        kind='point', 
        capsize=0.1, 
        palette='Set2', 
        height=4, 
        aspect=0.8
    )
    g3.fig.suptitle('DiDiD: Part-Time Probability (Workers Only)', y=1.02)

    # REGRESSION 4: Weekly Hours (Workers Only)
    g4 = sns.catplot(
        data=worker_viz_df, 
        x='Period', 
        y='HRSWORK1', 
        hue='Group', 
        col='lanham_quartile',
        kind='point', 
        capsize=0.1, 
        palette='Set2', 
        height=4, 
        aspect=0.8
    )
    g4.fig.suptitle('DiDiD: Weekly Hours (Workers Only)', y=1.02)

    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **DiDiD Coefficient & Visualization Interpretations**

    Each visualization panel shows **four quartiles of Lanham Act spending** (Q1 = lowest spending states, Q4 = highest spending states). Within each panel, we track two groups:
    - **Blue line (Treated)**: Mothers whose children qualified for Lanham Act childcare (ages 0-12 during 1943-1946)
    - **Red line (Control)**: Women without qualifying children (childless or older children)

    **The DiDiD effect is visible when:**
    1. The gap between blue and red lines **grows larger** from 1940->1950
    2. This gap expansion is **bigger in Q4 (high spending) than Q1 (low spending)**

    ### **Key Findings from the Visualizations**

    **Employment Probability (Regression 1):**
    - In **Q1 (Low Spending)**: The treated-control gap increases modestly from ~19pp to ~22pp
    - In **Q4 (High Spending)**: The gap expands dramatically from ~15pp to ~24pp
    - **Interpretation**: Universal childcare had a stronger employment effect in states that invested more heavily in the program, confirming the dose-response relationship predicted by the DiDiD model.

    **Weekly Hours - All Mothers (Regression 2):**
    - Control group (red) shows relatively stable hours across all spending quartiles (~18 hours/week)
    - Treated mothers in Q4 show the steepest increase: ~9 hours (1940) -> ~19 hours (1950)
    - **Interpretation**: Higher Lanham spending enabled mothers to not just enter the workforce, but work substantially more hours.

    **Part-Time Probability - Workers Only (Regression 3):**
    - Treated workers in **Q4** show declining part-time rates (25%->23%), while control workers decline even more (17%->12%)
    - The negative DiDiD suggests the effect is modest or non-existent
    - **Interpretation**: While the Lanham Act increased labor force entry, it did not strongly shift employed mothers from part-time to full-time work within high-spending states.

    **Weekly Hours - Workers Only (Regression 4):**
    - Among employed mothers, Q4 shows treated hours increasing from ~36->37 hours
    - The gradient effect (Q1→Q4) shows progressively larger increases in work intensity
    - **Interpretation**: Even mothers already in the workforce increased their hours commitment when affordable childcare became available, particularly in high-spending states.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #**Step 6: Overall Conclusions**

    ### **Summary of Key Findings**

    This analysis replicates and extends Herbst (2013)'s seminal study on the Lanham Act, the only universal childcare program in U.S. history. Using a difference-in-difference-in-differences (DiDiD) framework, we find:

    **1. Strong Evidence of Extensive Margin Effects (Herbst Replication)**
    - **DiDiD Coefficient (Employment)**: 0.00214***
      - A $43 increase in per-child spending (25th→75th percentile) increased maternal employment by **9.2 percentage points**
      - This represents a **58% increase** relative to the 1940 baseline (15.9%)
    - **DiDiD Coefficient (Hours)**: 0.09066***
      - The same spending increase raised weekly hours worked by **3.9 hours**
      - This is a **69% increase** from the pre-reform mean

    **2. Mixed Evidence on Intensive Margin Effects (McFarland Extension)**
    - **Part-Time Likelihood**: -0.00069** (statistically significant)
      - The Lanham Act DID significantly shift employed mothers from part-time to full-time work
      - This complements the strong extensive margin effects
    - **Hours (Workers Only)**: 0.03145***
      - Among already-employed mothers, higher spending increased hours by **1.35 hours/week**
      - Smaller effect than the full sample, suggesting the program primarily worked through labor force entry

    ### **Policy Implications**

    **What worked:**
    - Universal childcare dramatically increased labor force participation among mothers with young children and assisted in shifting already employed mothers to move from a part-time to full-time position
    - The program exhibited a clear **dose-response relationship**: states spending more saw bigger effects
    - Effects persisted 5 years post-program, suggesting lasting behavioral change

    ### **Limitations and Future Research**

    **Data constraints:**
    - We use a simplified model without the full demographic controls from the original paper
    - Results show directionally consistent but larger magnitudes than Herbst (2013)
    - Future work should incorporate education, marital status, and metro controls

    **Unanswered questions:**
    - Did quality variation within Lanham Act centers matter?
    - What happened to children's long-run outcomes (education, earnings)?
    - Would similar effects emerge in today's labor market?

    ### **Final Takeaway**

    The Lanham Act demonstrates that large-scale, affordable, universally-accessible childcare can fundamentally reshape maternal labor supply. However, childcare access alone is not sufficient to eliminate all gendered work patterns—complementary policies addressing workplace flexibility and cultural norms may be necessary to achieve full labor market equity.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
