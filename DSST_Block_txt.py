import pandas as pd
import os

# Load the DSST file
file_path = "CBAS0005_dsst_2025-02-13_10h51.49.847.csv"
df = pd.read_csv(file_path)

# Preserve empty rows to detect spacing-based blocks
df['stimulus_start_time'] = pd.to_numeric(df['stimulus_start_time'], errors='coerce')
df['stimulus_end_time'] = pd.to_numeric(df['stimulus_end_time'], errors='coerce')
df['SetNum'] = pd.to_numeric(df['SetNum'], errors='coerce')
df['block_start_time'] = pd.to_numeric(df['block_start_time'], errors='coerce')
df['block_end_time'] = pd.to_numeric(df['block_end_time'], errors='coerce')
df['SetType'] = df['SetType'].astype(str).str.strip().str.lower()
df.reset_index(drop=True, inplace=True)

# Function to split into blocks based on spacing (NaNs)
def get_blocks_from_spacing(df, set_num=None, set_type=None): 
    filtered = df.copy()
    #Preserve NaNs so we can detect block boundaries
    if set_num is not None and set_type is not None:
        filtered = filtered[
            ((filtered['SetNum'] == set_num) & (filtered['SetType'] == set_type)) |
            filtered['SetNum'].isna() |
            filtered['SetType'].isna()
    elif set_num is not None:
        filtered = filtered[(df['SetNum'] == set_num) | df['SetNum'].isna()]
    elif set_type is not None:
        filtered = filtered[(df['SetType'] == set_type) | df['SetType'].isna()]

    filtered = filtered.reset_index(drop=True)

    blocks = []
    current_block = []

    for _, row in filtered.iterrows():
        if pd.notna(row['SetNum']):
            current_block.append(row)
        elif current_block:
            blocks.append(pd.DataFrame(current_block))
            current_block = []
    if current_block:
        blocks.append(pd.DataFrame(current_block))

    timing_blocks = []
    for block in blocks:
        start = block['stimulus_start_time'].iloc[0]
        end = block['stimulus_end_time'].iloc[-1]
        duration = end - start
        if pd.notna(start) and pd.notna(duration):
            timing_blocks.append((start, duration, 1))

    return timing_blocks

# Build timing data for each condition
timing_data = {
    "SetNum_1_NR": get_blocks_from_spacing(df, set_num=1, set_type='nr'),
    "SetNum_1_R": get_blocks_from_spacing(df, set_num=1, set_type='r'),
    "SetNum_1_ALL": get_blocks_from_spacing(df, set_num=1),
    "SetNum_3": get_blocks_from_spacing(df, set_num=3),
    "SetNum_9": get_blocks_from_spacing(df, set_num=9),
}

# Save timing files
output_dir = "dsst_timing_files"
os.makedirs(output_dir, exist_ok=True)

for condition, timings in timing_data.items():
    with open(os.path.join(output_dir, f"{condition}.txt"), "w") as f:
        for onset, duration, modulation in timings:
            f.write(f"{onset:.3f} {duration:.3f} {modulation}\n")

print("All timing files created and saved to:", output_dir)

