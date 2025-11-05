import pandas as pd
import numpy as np
import unicodedata
import re
from rapidfuzz import fuzz
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter

# ------------------------- Constants ------------------------- #
DUTCH_PARTICLES = {"van", "de", "den", "der", "ten", "ter", "van de", "van den"}


# ------------------------- Functions ------------------------- #
def load_entity_data(entity_type: str = "people", data_dir: str = "./data/entities/") -> pd.DataFrame:
    """
    Load entity data from a CSV file.
    Args:
        entity_type (str): The type of entity to load (default: "people").
        data_dir (str): Directory containing the CSV files.
    Returns:
        pd.DataFrame: DataFrame containing entity data with columns including 'name'.
    """
    file_path = Path(data_dir) / f"{entity_type}.csv"
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} entities of type '{entity_type}'.")
    return df


def normalize_name(name: str) -> str:
    """
    Normalize a name string: lowercase, remove accents, punctuation, and extra spaces.
    Args:
        name (str): The name to normalize.
    Returns:
        str: Normalized name.
    """
    name = name.lower()
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def normalize_dutch_name(name: str) -> str:
    """
    Normalize a Dutch name and optionally remove common particles (tussenvoegsels).
    Args:
        name (str): The name to normalize.
    Returns:
        str: Normalized name with Dutch particles removed.
    """
    normalized = normalize_name(name)
    tokens = [t for t in normalized.split() if t not in DUTCH_PARTICLES]
    return " ".join(tokens)


def compute_similarity_matrix(names: list[str]) -> np.ndarray:
    """
    Compute a symmetric similarity matrix for a list of names using token_sort_ratio.
    Args:
        names (list[str]): List of names to compare.
    Returns:
        np.ndarray: n x n similarity matrix with values between 0 and 100.
    """
    n = len(names)
    sim_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            # score = fuzz.token_sort_ratio(normalize_dutch_name(names[i]), normalize_dutch_name(names[j]))
            score = fuzz.partial_ratio(normalize_dutch_name(names[i]), normalize_dutch_name(names[j]))
            sim_matrix[i, j] = sim_matrix[j, i] = score
    return sim_matrix


def hierarchical_clustering(sim_matrix: np.ndarray, distance_threshold: float = 0.15) -> np.ndarray:
    """
    Perform hierarchical clustering on a similarity matrix and assign cluster IDs.
    Args:
        sim_matrix (np.ndarray): n x n similarity matrix (0-100 scale).
        distance_threshold (float): Distance threshold to cut the dendrogram (0-1 scale).
    Returns:
        np.ndarray: Array of cluster IDs for each item.
    """
    # Convert similarity to distance (0-1 scale)
    dist_matrix = 1 - (sim_matrix / 100.0)
    np.fill_diagonal(dist_matrix, 0.0)

    # Convert to condensed distance matrix
    condensed_dist = squareform(dist_matrix)

    # Perform hierarchical clustering
    linkage_matrix = linkage(condensed_dist, method="average")
    cluster_ids = fcluster(linkage_matrix, t=distance_threshold, criterion="distance")
    return cluster_ids, linkage_matrix



def find_representative(df: pd.DataFrame, col_name: str = "canonical_name", cluster_col: str = "cluster_id", print_repr: bool = True):
    """
    Assign a representative name for each cluster.

    Args:
        df (pd.DataFrame): DataFrame with at least 'name' and cluster_col columns.
        cluster_col (str): Name of the column containing cluster IDs.

    Returns:
        pd.DataFrame: DataFrame with new column 'cluster_rep'.
    """

    # Ensure cluster IDs are numeric
    df[cluster_col] = df[cluster_col].astype(int)
    cluster_reps = {}

    for cid, group in df.groupby(cluster_col):   
        # most common     
        # representative = group['name'].value_counts().idxmax()

        # longest
        representative = group[col_name].loc[group[col_name].str.len().idxmax()]

        if print_repr:
            print(representative, ":\t", group[col_name].tolist())

        cluster_reps[cid] = representative

    # Map representatives back to DataFrame
    df["cluster_rep"] = df[cluster_col].map(cluster_reps)    
    
    return df



def save_clustered_data(df: pd.DataFrame, cluster_ids: np.ndarray, col_name: str = "canonical_name", output_path: str = "./data/structured_data/clustered_people.csv") -> None:
    """
    Add cluster IDs to DataFrame and save to CSV.

    Args:
        df (pd.DataFrame): Original DataFrame containing names.
        cluster_ids (np.ndarray): Cluster IDs corresponding to each row.
        output_path (str): Path to save the clustered CSV.
    """
    df["cluster_id"] = cluster_ids

    # find representative for each cluster
    df = find_representative(df, col_name=col_name)
    


    df.to_csv(output_path, index=False)
    num_clusters = len(df["cluster_id"].value_counts())
    print(f"There are {num_clusters} different clusters.")
    print(f"✅ Clustered data saved to '{output_path}'.")

    return df

def visualize_dendogram(df: pd.DataFrame, linkage_matrix, col_name: str = "canonical_name", output_file: str = "./pics/{entity_type}_dendrogram_highres.pdf"):
    # Assuming you already have linkage matrix Z and dataframe df
    plt.figure(figsize=(20, 10), dpi=300)   # <-- large figure + high DPI

    dendrogram(
        linkage_matrix,
        labels=df[col_name].values,
        leaf_rotation=90,
        leaf_font_size=8,       # smaller labels for long names
        color_threshold=0.2     # adjust if you want colored branches
    )

    plt.xlabel("Names", fontsize=12)
    plt.ylabel("Distance (1 - similarity)", fontsize=12)
    plt.title("Hierarchical Clustering of Names", fontsize=14)

    plt.tight_layout()

    # ---- Save in high quality ----
    plt.savefig(output_file, bbox_inches="tight")           # vector PDF
    # plt.savefig("dendrogram_highres.svg", bbox_inches="tight")           # vector SVG

    plt.close()   # closes the figure to free memory
    print(f"✅ Dendrogram saved as PDF to {output_file}")



# ------------------------- Main Workflow ------------------------- #
def group_entities(entity_type: str, col_name: str, data_dir: str, clustering_threshold: float = 0.15):

    output_file = f"{data_dir}/{entity_type}.csv"
    output_viz = f"{data_dir}/{entity_type}_dendrogram_highres.pdf"

    # Load data
    df = load_entity_data(entity_type=entity_type, data_dir=data_dir)

    # Compute similarity matrix
    names = df[col_name].tolist()

    # print(names)
    
    similarity_matrix = compute_similarity_matrix(names)

    # Perform hierarchical clustering
    cluster_ids, linkage_matrix = hierarchical_clustering(similarity_matrix, distance_threshold=clustering_threshold)

    # Save results
    df_with_cluster = save_clustered_data(df, cluster_ids, col_name, output_path=output_file)

    # Visualize clusters using dendogram
    visualize_dendogram(df, linkage_matrix, col_name, output_file=output_viz)

    return df_with_cluster


def cluster2attribute(
    df: pd.DataFrame, 
    cluster_col: str = 'cluster_id',
    filter_col: str = 'occupation'
):
    
    assert cluster_col in df.columns, f"The cluster_col (i.e. {cluster_col}) is not among the dataframe's columns."
    assert filter_col in df.columns, f"The filter_col (i.e. {filter_col}) is not among the dataframe's columns."
    
    if isinstance(df[filter_col][0], list):
        df[filter_col] = df[filter_col].apply(lambda x: x[0])
    
    cluster_filter = dict()

    for cluster_id, group in df.groupby(cluster_col):
        cluster_filter[cluster_id] = {
            'cluster_repr': group['cluster_rep'].tolist()[0],
            filter_col: list(set(group[filter_col].tolist()))[0][2:-2] if isinstance(list(set(group[filter_col].tolist()))[0], str) else list(set(group[filter_col].tolist()))[0]
        }
        # reprs = group['cluster_rep'].tolist()[0]
        # cluster_filter[reprs] = list(set(group[filter_col].tolist()))[0][2:-2] if isinstance(list(set(group[filter_col].tolist()))[0], str) else list(set(group[filter_col].tolist()))[0]

    return cluster_filter


def validate_cluster_attributes(
    df: pd.DataFrame,
    cluster_col: str = "cluster_id",
    list_columns: list[str] = [] ,
    filter_cols: list[str] = None
) -> pd.DataFrame:
    """
    Validate that all entities in the same cluster have the same non-null attribute values.
    Args:
        df (pd.DataFrame): Clustered DataFrame.
        cluster_col (str): Name of the column with cluster IDs.
        filter_cols (list[str]): Columns to take into account during validation.
    Returns:
        pd.DataFrame: A report of conflicts with columns:
                      [cluster_id, attribute, conflicting_values]
    """

    if not isinstance(filter_cols, list):
        filter_cols = [filter_cols]

    assert 'name' not in filter_cols, f"The column 'name' should not be among 'filter_cols'."

    conflict_records = []

    for cluster_id, group in df.groupby(cluster_col):
        for col in df.columns:
            
            if col not in filter_cols:
                continue
            
            # Drop nulls
            non_null_values = group[col].dropna()

            if non_null_values.empty:
                continue  # no data → no conflict            
            
            if col in list_columns:
                # Ensure all are Python lists
                lists = []
                for val in non_null_values:                    
                    lists.append(set(val))

                # Find intersection across all lists
                common_elements = set.intersection(*lists) if lists else set()

                if not common_elements:
                    conflict_records.append({
                        "cluster_id": cluster_id,
                        "attribute": col,
                        "conflicting_values": [list(l) for l in lists]
                    })

            else:
                # Scalar attributes: all non-null values must be the same
                unique_values = non_null_values.unique()
                if len(unique_values) > 1:
                    conflict_records.append({
                        "cluster_id": cluster_id,
                        "attribute": col,
                        "conflicting_values": list(unique_values)
                    })

    return pd.DataFrame(conflict_records)



if __name__ == "__main__":
    group_entities()
