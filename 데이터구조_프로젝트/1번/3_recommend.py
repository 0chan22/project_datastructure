"""
Battery Cathode Material Recommendation Engine

Usage:
  python 3_recommend.py LiCoO2                 # Top 5 for LiCoO2
  python 3_recommend.py LiCoO2 -k 10           # Top 10
  python 3_recommend.py --list                 # List all materials
  python 3_recommend.py --interactive          # Interactive mode
"""

import json
import os
import argparse
import sys
from typing import List, Tuple, Dict


class BatteryCathodeRecommender:
    """Battery cathode material recommendation engine"""
    
    def __init__(self, adjacency_list_path: str = 'adjacency_list.json'):
        """
        Initialize
        
        Args:
            adjacency_list_path: Path to adjacency list JSON
        """
        self.adjacency_list_path = adjacency_list_path
        self.graph = {}
    
    def load_graph(self) -> Dict[str, List[Dict]]:
        """Load adjacency list"""
        if not os.path.exists(self.adjacency_list_path):
            raise FileNotFoundError("Graph file not found: {}".format(self.adjacency_list_path))
        
        with open(self.adjacency_list_path, 'r', encoding='utf-8') as f:
            self.graph = json.load(f)
        
        print("[OK] Graph loaded: {} nodes".format(len(self.graph)))
        return self.graph
    
    def get_available_materials(self) -> List[str]:
        """Return all available materials"""
        return sorted(self.graph.keys())
    
    def recommend(self, target_formula: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Recommend substitute materials
        
        Args:
            target_formula: Target material name
            top_k: Top N recommendations
        
        Returns:
            [(material, similarity), ...] sorted by similarity descending
        """
        if target_formula not in self.graph:
            raise ValueError("Material '{}' not found".format(target_formula))
        
        neighbors = self.graph[target_formula]
        
        # Already sorted by similarity
        recommendations = [
            (neighbor['neighbor'], neighbor['similarity'])
            for neighbor in neighbors[:top_k]
        ]
        
        return recommendations
    
    def similarity_to_stars(self, similarity: float) -> str:
        """Convert similarity to star rating (0-5 stars)"""
        stars = int(round(similarity * 5))
        return '*' * stars
    
    def print_recommendation(self, target: str, top_k: int = 5):
        """Print recommendations"""
        try:
            recommendations = self.recommend(target, top_k)
            
            if not recommendations:
                print("No recommendations for '{}'".format(target))
                return
            
            print("\n" + "=" * 70)
            print("Recommendation for: {}".format(target))
            print("=" * 70)
            
            for rank, (material, similarity) in enumerate(recommendations, 1):
                stars = self.similarity_to_stars(similarity)
                percentage = "{:.1f}%".format(similarity * 100)
                print("{:2}. {:20} {} ({:>6})".format(rank, material, stars.ljust(5), percentage))
            
            print("=" * 70 + "\n")
        
        except ValueError as e:
            print("Error: {}".format(e))
    
    from typing import Optional

    def print_available_materials(self, limit: Optional[int] = None):
        """Print available materials list"""
        materials = self.get_available_materials()
        
        print("\n" + "=" * 70)
        print("Available Materials ({})".format(len(materials)))
        print("=" * 70)
        
        for i, material in enumerate(materials[:limit] if limit else materials, 1):
            neighbor_count = len(self.graph[material])
            print("{:3}. {:25} ({:2} similar)".format(i, material, neighbor_count))
        
        if limit and len(materials) > limit:
            print("... and {} more".format(len(materials) - limit))
        
        print("=" * 70 + "\n")
    
    def interactive_mode(self):
        """Interactive recommendation mode"""
        print("\n" + "=" * 70)
        print("Battery Cathode Recommendation Engine (Interactive Mode)")
        print("=" * 70)
        print("Commands:")
        print("  1. Get recommendations (enter material name)")
        print("  2. List all materials")
        print("  3. Exit")
        print("=" * 70 + "\n")
        
        while True:
            try:
                choice = input("Select (1-3): ").strip()
                
                if choice == '1':
                    target = input("Material name (e.g., LiCoO2): ").strip()
                    if not target:
                        print("Please enter material name")
                        continue
                    
                    try:
                        k = input("Number of recommendations (default 5): ").strip()
                        k = int(k) if k else 5
                    except ValueError:
                        k = 5
                    
                    self.print_recommendation(target, top_k=k)
                
                elif choice == '2':
                    try:
                        limit = input("Number to display (default all): ").strip()
                        limit = int(limit) if limit else None
                    except ValueError:
                        limit = None
                    
                    self.print_available_materials(limit)
                
                elif choice == '3':
                    print("Exiting...")
                    break
                
                else:
                    print("Select 1-3")
            
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print("Error: {}".format(e))


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Battery Cathode Material Recommendation Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 3_recommend.py LiCoO2              # Top 5 for LiCoO2
  python 3_recommend.py LiCoO2 -k 10        # Top 10
  python 3_recommend.py --list              # List materials
  python 3_recommend.py --interactive       # Interactive mode
  python 3_recommend.py --graph custom.json # Custom graph
        """
    )
    
    parser.add_argument('target', nargs='?', help='Target material name')
    parser.add_argument('-k', '--top', type=int, default=5, dest='top_k', help='Number of recommendations (default: 5)')
    parser.add_argument('--list', action='store_true', help='List all materials')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--graph', default='adjacency_list.json', help='Adjacency list file path')
    
    args = parser.parse_args()
    
    # Check graph file
    if not os.path.exists(args.graph):
        print("Graph file not found: {}".format(args.graph))
        print("Run 2_processing.py first")
        sys.exit(1)
    
    # Initialize recommender
    recommender = BatteryCathodeRecommender(args.graph)
    recommender.load_graph()
    
    # Execute command
    if args.interactive:
        recommender.interactive_mode()
    elif args.list:
        recommender.print_available_materials()
    elif args.target:
        recommender.print_recommendation(args.target, top_k=args.top_k)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
