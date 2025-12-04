# 배터리 양극재 추천 시스템

배터리 양극재(Cathode Materials)의 대체 재료를 그래프 기반으로 추천하는 시스템입니다.

## 📋 프로젝트 구조

```
1번/
├── 1_dataload.py           # 데이터 로드 (배터리 양극재)
├── 2_processing.py         # 유사도 계산 (3가지 메트릭)
├── 3_recommend.py          # 추천 엔진 (대체 재료)
├── battery_cathodes.json   # 원본 데이터
├── adjacency_list.json     # 유사도 그래프
└── README.md               # 이 파일
```

## 🚀 실행 방법

### 1단계: 데이터 로드
```bash
python 1_dataload.py
```

### 2단계: 유사도 계산
```bash
python 2_processing.py
```

### 3단계: 추천 조회
```bash
# 재료 목록 보기
python 3_recommend.py --list

# 특정 재료 추천 (예: LiCoO2의 상위 5개)
python 3_recommend.py LiCoO2

# 상위 10개
python 3_recommend.py LiCoO2 -k 10

# 대화형 모드
python 3_recommend.py --interactive
```

## 📊 특성 및 가중치

### 특성 (Feature)
| 특성 | 가중치 |
|------|--------|
| 밀도 (Density) | 40% |
| 부피 (Volume) | 30% |
| 형성에너지 (Formation Energy) | 20% |
| 밴드갭 (Band Gap) | 10% |

### 유사도 메트릭
| 메트릭 | 가중치 | 설명 |
|--------|--------|------|
| 유클리드 거리 | 25% | 정규화 특성 간 거리 역함수 |
| 코사인 유사도 | 50% | 벡터 각도 유사성 |
| 구조 유사도 | 25% | 밴드갭과 밀도 가우시안 커널 |

## 💡 사용 예

```bash
# 예시 1: LiCoO2의 상위 3개 대체재 추천
python 3_recommend.py LiCoO2 -k 3

# 예시 2: 전체 재료 목록 확인
python 3_recommend.py --list

# 예시 3: 대화형으로 여러 번 추천 조회
python 3_recommend.py --interactive
```

## 📈 데이터 흐름

```
battery_cathodes.json (원본 데이터)
         ↓
    [1_dataload.py]
         ↓
    [2_processing.py]
         ↓
    adjacency_list.json (그래프)
         ↓
    [3_recommend.py]
         ↓
    추천 결과 (⭐ 별점 표시)
```

## 🔧 커스터마이징

### 특성 가중치 변경
`2_processing.py`의 `FEATURE_WEIGHTS`:
```python
FEATURE_WEIGHTS = {
    'density': 0.4,        # 40% → 더 높이거나 낮추기
    'volume': 0.3,
    'formation_energy_per_atom': 0.2,
    'band_gap': 0.1
}
```

### 유사도 메트릭 가중치 변경
`2_processing.py`의 `SIMILARITY_WEIGHTS`:
```python
SIMILARITY_WEIGHTS = {
    'euclidean': 0.25,     # 25%
    'cosine': 0.5,         # 50% (가장 중요)
    'structural': 0.25     # 25%
}
```

### 유사도 임계값 변경
`2_processing.py`에서 `0.85` 값 조정:
```python
if sim >= 0.85:  # 값이 높을수록 엄격한 필터
```

## 📌 명령어 참고

```bash
python 3_recommend.py [대상재료] [옵션]

옵션:
  -k, --top INT      추천 개수 (기본값: 5)
  --list             사용 가능한 재료 목록
  --interactive      대화형 모드
  --graph PATH       커스텀 그래프 파일
```

## 🎯 예상 출력

```
======================================================================
대체재료 추천: LiCoO2
======================================================================
1. LiFePO4           ⭐⭐⭐⭐⭐ ( 95.3%)
2. LiMnO2            ⭐⭐⭐⭐⭐ ( 92.1%)
3. LiNiO2            ⭐⭐⭐⭐  ( 87.6%)
4. LiNi0.5Mn1.5O4    ⭐⭐⭐⭐  ( 82.4%)
5. LiMn2O4           ⭐⭐⭐   ( 78.9%)
======================================================================
```

---

**개발자**: 배터리 재료 추천 시스템 팀  
**버전**: 1.0  
**라이선스**: 학습/연구용
