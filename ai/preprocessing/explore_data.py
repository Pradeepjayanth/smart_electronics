import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for plots
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

def load_dataset():
    """Loads the AI4I 2020 dataset from the dataset directory."""
    # Resolve absolute path relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try the correct filename 'ai4i2020.csv' first, fallback to user's 'ai412020.csv'
    possible_paths = [
        os.path.join(script_dir, "../dataset/ai4i2020.csv"),
        os.path.join(script_dir, "../dataset/ai412020.csv")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Loading dataset from: {path}")
            return pd.read_csv(path)
            
    raise FileNotFoundError(
        f"Dataset not found. Tried paths: {[os.path.abspath(p) for p in possible_paths]}"
    )

def explore_basic_info(df):
    """Prints shape, basic information, and missing values."""
    print("=" * 60)
    print("1. BASIC DATASET INFORMATION")
    print("=" * 60)
    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    
    print("Data Types & Null Counts:")
    print(df.info())
    
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("\nNo missing values found in the dataset.")
    else:
        print("\nMissing Values:")
        print(missing[missing > 0])
    print("\n")

def explore_target_distribution(df):
    """Explores the machine failure distribution and failure modes."""
    print("=" * 60)
    print("2. TARGET DISTRIBUTION & FAILURE MODES")
    print("=" * 60)
    
    target_counts = df['Machine failure'].value_counts()
    target_pct = df['Machine failure'].value_counts(normalize=True) * 100
    
    print("Machine Failure Class Distribution:")
    for val in target_counts.index:
        status = "Fail" if val == 1 else "No Fail"
        print(f"  {status} ({val}): {target_counts[val]} instances ({target_pct[val]:.2f}%)")
    
    # Failure Modes
    failure_modes = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    print("\nSpecific Failure Modes Counts:")
    for mode in failure_modes:
        if mode in df.columns:
            count = df[mode].sum()
            pct = (count / len(df)) * 100
            print(f"  {mode} (Tool Wear/Heat/Power/Overstrain/Random): {count} instances ({pct:.2f}%)")
    print("\n")

def plot_and_save_visualizations(df, output_dir):
    """Generates and saves exploratory plots."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving visualizations to: {os.path.abspath(output_dir)}")
    
    # 1. Target Class Imbalance Plot
    plt.figure()
    sns.countplot(x='Machine failure', data=df, hue='Machine failure', palette='Set2', legend=False)
    plt.title('Machine Failure Distribution')
    plt.xlabel('Machine Failure (0 = No, 1 = Yes)')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, 'failure_distribution.png'))
    plt.close()
    
    # 2. Numerical Features Distributions
    num_cols = [
        'Air temperature [K]', 
        'Process temperature [K]', 
        'Rotational speed [rpm]', 
        'Torque [Nm]', 
        'Tool wear [min]'
    ]
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    axes = axes.ravel()
    
    for i, col in enumerate(num_cols):
        sns.histplot(data=df, x=col, hue='Machine failure', kde=True, ax=axes[i], multiple='stack', palette='Set1')
        axes[i].set_title(f'Distribution of {col}')
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Count')
        
    # Remove the empty subplot
    fig.delaxes(axes[-1])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'numerical_features_distribution.png'))
    plt.close()
    
    # 3. Correlation Heatmap
    corr_cols = num_cols + ['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    plt.figure(figsize=(10, 8))
    corr_matrix = df[corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Feature & Failure Mode Correlation Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'))
    plt.close()
    
    # 4. Boxplots to visualize features vs failure
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.ravel()
    for i, col in enumerate(num_cols):
        sns.boxplot(x='Machine failure', y=col, data=df, hue='Machine failure', ax=axes[i], palette='Set2', legend=False)
        axes[i].set_title(f'{col} vs Machine Failure')
        axes[i].set_xlabel('Machine Failure')
        axes[i].set_ylabel(col)
        
    fig.delaxes(axes[-1])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'features_vs_failure_boxplots.png'))
    plt.close()
    print("Visualizations saved successfully!\n")

def print_insights(df):
    """Prints key findings from standard analysis."""
    print("=" * 60)
    print("3. KEY DATASET INSIGHTS")
    print("=" * 60)
    
    num_cols = [
        'Air temperature [K]', 
        'Process temperature [K]', 
        'Rotational speed [rpm]', 
        'Torque [Nm]', 
        'Tool wear [min]'
    ]
    
    # Print mean value differences for Fail vs No Fail
    print("Average feature values for Normal vs Failure states:")
    grouped = df.groupby('Machine failure')[num_cols].mean().T
    grouped.columns = ['Normal (0)', 'Failure (1)']
    grouped['Difference (%)'] = ((grouped['Failure (1)'] - grouped['Normal (0)']) / grouped['Normal (0)']) * 100
    print(grouped.round(2))
    print("\nObservations:")
    print("- Failures tend to occur at higher average air and process temperatures.")
    print("- Failures show significantly higher average Torque and Tool wear.")
    print("- Rotational speed is lower on average during failures (often inversely correlated with Torque).")
    print("=" * 60)

def main():
    try:
        df = load_dataset()
        
        # 1. Print Basic Info
        explore_basic_info(df)
        
        # 2. Target/Class Distributions
        explore_target_distribution(df)
        
        # 3. Print average feature value differences (Insights)
        print_insights(df)
        
        # 4. Generate and save plots
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_plots_dir = os.path.join(script_dir, 'plots')
        plot_and_save_visualizations(df, output_plots_dir)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()