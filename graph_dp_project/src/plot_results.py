import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results():
    # Load results
    results_path = os.path.join(os.path.dirname(__file__), '../paper/results_comprehensive.csv')
    df = pd.read_csv(results_path)
    
    # Set style
    sns.set_theme(style="whitegrid")
    
    # Filter for Facebook graph
    df = df[df['graph'] == 'Facebook_Sample']
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '../paper/plots')
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Triangle Count Comparison (Clipped vs Smooth)
    plt.figure(figsize=(10, 6))
    tri_df = df[df['metric'].str.contains('TriangleCount')]
    sns.lineplot(data=tri_df, x='epsilon', y='rel_error', hue='metric', marker='o')
    plt.title('Triangle Count Error: Clipped vs Smooth Sensitivity')
    plt.ylabel('Relative Error')
    plt.xlabel('Epsilon')
    plt.yscale('log')
    plt.savefig(os.path.join(output_dir, 'triangle_error.png'))
    plt.close()
    
    # Plot 2: 2-Star Count Comparison (Clipped vs Smooth)
    plt.figure(figsize=(10, 6))
    star_df = df[df['metric'].str.contains('2-StarCount')]
    sns.lineplot(data=star_df, x='epsilon', y='rel_error', hue='metric', marker='o')
    plt.title('2-Star Count Error: Clipped vs Smooth Sensitivity')
    plt.ylabel('Relative Error')
    plt.xlabel('Epsilon')
    plt.yscale('log')
    plt.savefig(os.path.join(output_dir, 'kstar_error.png'))
    plt.close()

    # Plot 3: Edge Count Error
    plt.figure(figsize=(10, 6))
    edge_df = df[df['metric'] == 'EdgeCount']
    sns.lineplot(data=edge_df, x='epsilon', y='rel_error', marker='o', color='green')
    plt.title('Edge Count Error')
    plt.ylabel('Relative Error')
    plt.xlabel('Epsilon')
    plt.yscale('log')
    plt.savefig(os.path.join(output_dir, 'edge_error.png'))
    plt.close()

    print(f"Plots saved to {output_dir}")

if __name__ == "__main__":
    plot_results()
