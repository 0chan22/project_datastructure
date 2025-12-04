"""
배터리 양극재 데이터 로드

기존 materials_data.csv 또는 테스트 데이터에서 Li 함유 양극재 추출
"""

import os
import json
import random
from typing import List, Dict, Any


class BatteryCathodeMaterialLoader:
    """배터리 양극재 데이터를 로드하는 클래스"""
    
    def __init__(self):
        """초기화"""
        self.materials = []
    
    def load_from_csv(self, csv_file: str = 'materials_data.csv', limit: int = 100) -> List[Dict[str, Any]]:
        """
        CSV 파일에서 Li 함유 양극재 로드
        
        Args:
            csv_file: CSV 파일 경로
            limit: 로드 제한
        
        Returns:
            재료 리스트
        """
        try:
            import pandas as pd
            
            if not os.path.exists(csv_file):
                print(f"⚠️  {csv_file} 없음. 테스트 데이터 생성합니다.")
                return self._generate_test_data(limit)
            
            df = pd.read_csv(csv_file)
            
            # Li 함유 물질 필터링
            df_li = df[df['formula'].str.contains('Li', case=False, na=False)].copy()
            
            # 필요한 컬럼 확인
            required_cols = ['formula', 'density', 'band_gap']
            for col in required_cols:
                if col not in df_li.columns:
                    print(f"⚠️  컬럼 '{col}' 없음.")
                    return self._generate_test_data(limit)
            
            # NaN 제거
            df_li = df_li.dropna(subset=['density', 'band_gap'])
            
            # 데이터 변환
            materials = []
            for idx, (_, row) in enumerate(df_li.head(limit).iterrows()):
                mat_dict = {
                    'material_id': row.get('material_id', f'mp-{1000+idx}'),
                    'formula': str(row['formula']),
                    'density': float(row['density']),
                    'band_gap': float(row['band_gap']),
                    'formation_energy_per_atom': float(row.get('formation_energy_per_atom', 0.0)) if 'formation_energy_per_atom' in row else 0.0,
                    'volume': float(row.get('volume', 100.0)) if 'volume' in row else 100.0,
                }
                materials.append(mat_dict)
            
            self.materials = materials
            print(f"✓ {len(materials)}개 재료 로드됨 ({csv_file}에서)")
            return materials
        
        except ImportError:
            print("⚠️  pandas가 필요합니다. 테스트 데이터로 진행합니다.")
            return self._generate_test_data(limit)
        except Exception as e:
            print(f"✗ CSV 로드 실패: {e}")
            return self._generate_test_data(limit)
    
    def _generate_test_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """테스트용 샘플 데이터 생성"""
        
        formulas = [
            'LiCoO2', 'LiNiO2', 'LiMnO2', 'Li2MnO3',
            'LiNi0.8Co0.15Al0.05O2', 'LiNi0.5Co0.2Mn0.3O2',
            'LiFePO4', 'LiMnPO4', 'LiCoPO4',
            'LiMn2O4', 'LiNi0.5Mn1.5O4', 'LiMnO2',
            'Li(NiMnCo)O2', 'LiVO2', 'LiTiO2',
            'LiNbO3', 'LiNiPO4', 'LiFeO2'
        ]
        
        materials = []
        for i in range(min(limit, 80)):
            idx = i % len(formulas)
            formula = formulas[idx]
            if i >= len(formulas):
                formula = f"{formula}_{i // len(formulas)}"
            
            mat_dict = {
                'material_id': f'mp-{10000 + i}',
                'formula': formula,
                'density': round(random.uniform(2.5, 5.5), 2),
                'band_gap': round(random.uniform(0.2, 4.5), 2),
                'formation_energy_per_atom': round(random.uniform(-4.0, 0.5), 3),
                'volume': round(random.uniform(50.0, 200.0), 1),
            }
            materials.append(mat_dict)
        
        self.materials = materials
        print(f"✓ {len(materials)}개 테스트 재료 생성됨")
        return materials
    
    def save_to_json(self, data: List[Dict[str, Any]], output_path: str = 'battery_cathodes.json'):
        """JSON으로 저장"""
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # 카테고리별로 분류 (간단한 분류)
        output = {
            'LCO': [m for m in data if 'Co' in m['formula'] and 'Mn' not in m['formula']],
            'NCM': [m for m in data if 'Ni' in m['formula'] and 'Mn' in m['formula']],
            'LFP': [m for m in data if 'Fe' in m['formula'] and 'P' in m['formula']],
            'General': data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 데이터 저장됨: {output_path}")


def main():
    """메인 실행 함수"""
    
    print("=" * 70)
    print("배터리 양극재 데이터 로드")
    print("=" * 70)
    
    # 로더 초기화
    loader = BatteryCathodeMaterialLoader()
    
    # 데이터 로드 (CSV 또는 테스트)
    materials = loader.load_from_csv(limit=100)
    
    # 저장
    loader.save_to_json(materials, 'battery_cathodes.json')
    
    # 요약
    print("\n" + "=" * 70)
    print("로드 완료 요약")
    print("=" * 70)
    print(f"총 {len(materials)}개 재료")
    print(f"  - 밀도 범위: {min(m['density'] for m in materials):.2f} ~ {max(m['density'] for m in materials):.2f}")
    print(f"  - 밴드갭 범위: {min(m['band_gap'] for m in materials):.2f} ~ {max(m['band_gap'] for m in materials):.2f}")
    
    print("\n샘플 데이터:")
    for mat in materials[:5]:
        print(f"  - {mat['formula']:20} (밀도: {mat['density']:.2f}, 밴드갭: {mat['band_gap']:.2f})")
    
    print(f"\n✓ 다음 단계: python 2_processing.py")


if __name__ == '__main__':
    main()
