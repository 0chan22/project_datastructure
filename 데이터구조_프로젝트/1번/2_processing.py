"""
배터리 양극재 데이터 전처리 및 유사도 계산
"""

import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

print("=" * 70)
print("Battery Cathode Material - Preprocessing & Similarity")
print("=" * 70)

# === 1. Data Load ===
data_path = 'battery_cathodes.json'
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Merge categories
all_materials = []
if isinstance(data, dict):
    for category, materials in data.items():
        if isinstance(materials, list):
            all_materials.extend(materials)
else:
    all_materials = data

# Remove duplicates
seen_ids = set()
materials = []
for mat in all_materials:
    mat_id = mat.get('material_id', 'unknown')
    if mat_id not in seen_ids:
        seen_ids.add(mat_id)
        materials.append(mat)

print("[OK] {} unique materials loaded".format(len(materials)))

# === 2. Feature Extraction & Normalization ===
print("\n[Preprocessing] Feature extraction & normalization...")

IMPORTANT_FEATURES = ['density', 'band_gap', 'formation_energy_per_atom', 'volume']
FEATURE_WEIGHTS = {
    'density': 0.4,
    'volume': 0.3,
    'formation_energy_per_atom': 0.2,
    'band_gap': 0.1
}

feature_matrix = []
valid_materials = []
material_to_idx = {}
idx_to_material = {}

for mat in materials:
    features = []
    valid = True
    
    for feature in IMPORTANT_FEATURES:
        value = mat.get(feature)
        if value is None:
            valid = False
            break
        try:
            features.append(float(value))
        except:
            valid = False
            break
    
    if valid and len(features) == 4:
        feature_matrix.append(features)
        idx = len(valid_materials)
        formula = mat.get('formula', 'Material_{}'.format(idx))
        material_to_idx[formula] = idx
        idx_to_material[idx] = formula
        valid_materials.append(mat)

print("[OK] {} materials used".format(len(valid_materials)))

# Normalize
if len(feature_matrix) == 0:
    print("[ERROR] No valid data")
    exit(1)

feature_matrix = np.array(feature_matrix, dtype=float)
scaler = MinMaxScaler()
normalized_features = scaler.fit_transform(feature_matrix)

print("[OK] {} materials normalized".format(len(normalized_features)))

# === 3. Similarity Calculation ===
print("\n[Similarity] Calculating...")
n = len(normalized_features)

def euclidean_sim(i, j):
    vec_i = normalized_features[i]
    vec_j = normalized_features[j]
    weighted_diff = np.array([
        (vec_i[k] - vec_j[k]) ** 2 * FEATURE_WEIGHTS[IMPORTANT_FEATURES[k]]
        for k in range(4)
    ])
    dist = np.sqrt(np.sum(weighted_diff))
    return 1.0 / (1.0 + dist)

def cosine_sim(i, j):
    vec_i = normalized_features[i].reshape(1, -1)
    vec_j = normalized_features[j].reshape(1, -1)
    return float(cosine_similarity(vec_i, vec_j)[0, 0])

def structural_sim(i, j):
    mat_i = valid_materials[i]
    mat_j = valid_materials[j]
    
    bg_i = mat_i.get('band_gap', 2.0)
    bg_j = mat_j.get('band_gap', 2.0)
    bg_sim = np.exp(-abs(bg_i - bg_j) / 0.5)
    
    rho_i = mat_i.get('density', 3.0)
    rho_j = mat_j.get('density', 3.0)
    if rho_i > 0 and rho_j > 0:
        rho_sim = np.exp(-abs(np.log(rho_i / rho_j)) / 0.2)
    else:
        rho_sim = 0.5
    
    return (bg_sim + rho_sim) / 2.0

SIMILARITY_WEIGHTS = {
    'euclidean': 0.25,
    'cosine': 0.5,
    'structural': 0.25
}

def hybrid_sim(i, j):
    e_sim = euclidean_sim(i, j)
    c_sim = cosine_sim(i, j)
    s_sim = structural_sim(i, j)
    return (SIMILARITY_WEIGHTS['euclidean'] * e_sim +
            SIMILARITY_WEIGHTS['cosine'] * c_sim +
            SIMILARITY_WEIGHTS['structural'] * s_sim)

# Build adjacency list
adjacency = {}
similarities = []

for i in range(n):
    neighbors = []
    for j in range(n):
        if i != j:
            sim = hybrid_sim(i, j)
            similarities.append(sim)
            if sim >= 0.85:
                neighbors.append({
                    'neighbor': idx_to_material[j],
                    'similarity': round(sim, 4)
                })
    
    neighbors.sort(key=lambda x: x['similarity'], reverse=True)
    formula_i = idx_to_material[i]
    adjacency[formula_i] = neighbors
    
    if (i + 1) % max(1, n // 5) == 0:
        print("  {}/{} done...".format(i + 1, n))

print("[OK] Adjacency list created")

# Auto-adjust threshold
avg_neighbors = np.mean([len(neighbors) for neighbors in adjacency.values()])
print("\n[Threshold] init=0.85, avg_neighbors={:.1f}".format(avg_neighbors))

if avg_neighbors < 5:
    all_sims = sorted(similarities)
    target_idx = int(len(all_sims) * 0.8)
    new_threshold = all_sims[max(0, min(target_idx, len(all_sims)-1))]
    print("  -> Auto adjust: {:.4f}".format(new_threshold))
    
    # Recalculate
    adjacency = {}
    for i in range(n):
        neighbors = []
        for j in range(n):
            if i != j:
                sim = hybrid_sim(i, j)
                if sim >= new_threshold:
                    neighbors.append({
                        'neighbor': idx_to_material[j],
                        'similarity': round(sim, 4)
                    })
        neighbors.sort(key=lambda x: x['similarity'], reverse=True)
        adjacency[idx_to_material[i]] = neighbors

# === 4. Save ===
with open('adjacency_list.json', 'w', encoding='utf-8') as f:
    json.dump(adjacency, f, indent=2, ensure_ascii=False)

print("[OK] Adjacency list saved: adjacency_list.json")

# === 5. Statistics ===
print("\n" + "=" * 70)
print("Graph Statistics")
print("=" * 70)
num_nodes = len(adjacency)
num_edges = sum(len(neighbors) for neighbors in adjacency.values())
avg_degree = num_edges / num_nodes if num_nodes > 0 else 0

print("Nodes (Materials): {}".format(num_nodes))
print("Edges (Connections): {}".format(num_edges))
print("Avg Degree: {:.2f}".format(avg_degree))

# Sample output
print("\n" + "=" * 70)
print("Sample Adjacency List")
print("=" * 70)
for i, (formula, neighbors) in enumerate(list(adjacency.items())[:3]):
    print("\n{}:".format(formula))
    for neighbor in neighbors[:3]:
        print("  -> {}: {}".format(neighbor['neighbor'], neighbor['similarity']))
    if len(neighbors) > 3:
        print("  ... and {} more".format(len(neighbors) - 3))

print("\n[OK] Complete! Next: python 3_recommend.py")
