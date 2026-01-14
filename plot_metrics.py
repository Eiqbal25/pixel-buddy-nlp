import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_metrics(csv_file="experiment_metrics.csv"):
    # --- CONFIGURATION ---
    # Define the specific results folder path
    results_dir = r"C:\Pixel Buddy Soccer Assistant - worldwide\results"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(results_dir):
        try:
            os.makedirs(results_dir)
            print(f"📂 Created results folder: {results_dir}")
        except OSError as e:
            print(f"❌ Error creating folder: {e}")
            return

    # 1. Check if CSV data exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found. Run the assistant and ask some questions first!")
        return

    # 2. Load Data
    try:
        df = pd.read_csv(csv_file)
        if len(df) < 3:
            print("⚠️  Not enough data to plot. Please ask at least 3-5 questions to get good graphs.")
            return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    print(f"📊 Analyzing {len(df)} interactions...")

    # Set style for professional look
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12})

    # ==========================================
    # CHART 1: Average Response Time Breakdown
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    # Calculate averages
    avg_times = df[['stt_time', 'nlp_time', 'tts_time']].mean()
    
    # Create stacked bar chart
    bottom = 0
    colors = ['#FFB74D', '#64B5F6', '#81C784'] # Orange (STT), Blue (NLP), Green (TTS)
    labels = ['Speech Recognition', 'AI Processing (RAG)', 'Text-to-Speech']
    
    for i, col in enumerate(avg_times.index):
        plt.bar('Average Interaction', avg_times[col], bottom=bottom, color=colors[i], label=labels[i], width=0.5)
        # Add text label in middle of bar
        if avg_times[col] > 0.1:
            plt.text('Average Interaction', bottom + avg_times[col]/2, f"{avg_times[col]:.2f}s", 
                     ha='center', va='center', color='black', fontweight='bold')
        bottom += avg_times[col]

    plt.title('System Latency Breakdown (Average)', fontsize=14, fontweight='bold')
    plt.ylabel('Time (seconds)')
    plt.legend(loc='upper right')
    plt.grid(axis='x')
    
    # Save to specific folder
    output_path = os.path.join(results_dir, 'plot_breakdown.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved breakdown to: {output_path}")

    # ==========================================
    # CHART 2: Voice vs. Text Speed Comparison
    # ==========================================
    plt.figure(figsize=(8, 6))
    
    # Filter valid inputs
    voice_df = df[df['input_type'] == 'voice']
    text_df = df[df['input_type'] == 'text']
    
    if not voice_df.empty and not text_df.empty:
        data = [voice_df['total_response_time'], text_df['total_response_time']]
        plt.boxplot(data, labels=['Voice Input', 'Text Input'], patch_artist=True,
                   boxprops=dict(facecolor='#E1F5FE'))
        
        plt.title('Total Response Time: Voice vs. Text', fontsize=14, fontweight='bold')
        plt.ylabel('Total Seconds')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        output_path = os.path.join(results_dir, 'plot_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved comparison to: {output_path}")
    else:
        print("⚠️  Skipping Comparison Plot (need both Voice and Text data)")

    # ==========================================
    # CHART 3: Processing Time vs. Query Length
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    sns.scatterplot(data=df, x='query_length', y='nlp_time', hue='input_type', s=100)
    
    # Add trendline
    if len(df) > 1:
        sns.regplot(data=df, x='query_length', y='nlp_time', scatter=False, color='grey', line_kws={'alpha':0.5})

    plt.title('AI Processing Scalability', fontsize=14, fontweight='bold')
    plt.xlabel('Query Length (characters)')
    plt.ylabel('NLP Processing Time (seconds)')
    
    output_path = os.path.join(results_dir, 'plot_scalability.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved scalability to: {output_path}")
    
    print("\n🎉 All plots generated!")

if __name__ == "__main__":
    plot_metrics()