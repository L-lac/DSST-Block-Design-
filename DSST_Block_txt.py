import pandas as pd
import os

# Load the DSST file
file_path = "your_file_path.csv"
df = pd.read_csv(file_path)

# Clean and prepare the dataset
df = df[df['CondsFile'].notna()].copy()
df['stimulus_start_time'] = pd.to_numeric(df['stimulus_start_time'], errors='coerce')
df['stimulus_end_time'] = pd.to_numeric(df['stimulus_end_time'], errors='coerce')
df['SetNum'] = pd.to_numeric(df['SetNum'], errors='coerce')
df['block_start_time'] = pd.to_numeric(df['block_start_time'], errors='coerce')
df['block_end_time'] = pd.to_numeric(df['block_end_time'], errors='coerce')
df['SetType'] = df['SetType'].astype(str).str.strip().str.lower()
df.reset_index(drop=True, inplace=True)

def get_timing_file(df, set_num=None, set_type=None):
    if set_num is not None:
        df = df[df['SetNum'] == set_num]
    if set_type is not None:
        df = df[df['SetType'] == set_type]

    timing_blocks = []
    for block_id, block_df in df.groupby('CondsFile'):
        block_df = block_df.sort_values('stimulus_start_time')
        start = block_df['stimulus_start_time'].iloc[0]
        end = block_df['stimulus_end_time'].iloc[-1]
        duration = end - start
        if pd.notna(start) and pd.notna(duration):
            timing_blocks.append((start, duration, 1))
    return timing_blocks

# Create timing data
timing_data = {
    "SetNum_1_NR": get_timing_file(df, set_num=1, set_type='nr'),
    "SetNum_1_R": get_timing_file(df, set_num=1, set_type='r'),
    "SetNum_1_ALL": get_timing_file(df, set_num=1),
    "SetNum_3": get_timing_file(df, set_num=3),
    "SetNum_9": get_timing_file(df, set_num=9)
}

# Save output
output_dir = "dsst_timing_files"
os.makedirs(output_dir, exist_ok=True)
for condition, timings in timing_data.items():
    with open(os.path.join(output_dir, f"{condition}.txt"), "w") as f:
        for onset, duration, modulation in timings:
            f.write(f"{onset:.3f} {duration:.3f} {modulation}\n")

