import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

## 전처리된 데이터 가져오기
path_file_drug = './전처리된 데이터/투약기록_2군제거.xlsx'
path_file_c_egc = './전처리된 데이터/CEL1.xlsx' #Clinical_EGC_sheet합침
path_file_hw = './전처리된 데이터/키_몸무게2.xlsx'
path_file_smoke = './전처리된 데이터/흡연정보2.xlsx' 
path_file_egc = './전처리된 데이터/EGC_main.xlsx'

df_drug = pd.read_excel(path_file_drug)
df_c_egc = pd.read_excel(path_file_c_egc)
df_hw = pd.read_excel(path_file_hw)
df_smoke = pd.read_excel(path_file_smoke)
df_egc = pd.read_excel(path_file_egc)

### 전처리 1차 - 환자별 채혈/채뇨 기록, 키/몸무게 기록, 흡연기록, 투약기록,  EGC data 가로로 concat

## 환자명 제거
df_hw.drop('환자명',axis=1, inplace=True)
df_smoke.drop('환자명',axis=1, inplace=True)
df_egc.drop('이름',axis=1, inplace=True)
df_drug.drop('환자명',axis=1, inplace=True)

## 중복되는 컬럼명 수정
df_drug.rename(columns={'처방코드':'투약기록_처방코드'}, inplace=True)
df_c_egc.rename(columns={'처방코드':'C_EGC_처방코드'}, inplace=True)
df_hw.rename(columns={'기록일시':'키-몸무게_기록일시'}, inplace=True)
df_smoke.rename(columns={'기록일시':'흡연_기록일시'}, inplace=True)

## 등록번호별로 데이터 갖고오기
for j in df_egc.iloc[1:,5] : # 한 줄 데이터에서 등록번호 가져오기
    
    # 채혈,채뇨검사(기준 data)
    st = 0
    tmp=0 # 데이터 개수
    for cnt, i in enumerate(df_c_egc.iloc[:,2]) : # cnt는 0부터 시작
        if i == j :
            if tmp == 0 :
                st=cnt
            tmp+=1
        else :
            if tmp > 0 :
                break
            st=cnt   
    
    # 키-몸무게             
    st2 = 0
    tmp2=0
    for cnt, i in enumerate(df_hw.iloc[:,0]) :
        if i == j :
            if tmp2 == 0:
                st2 = cnt
            tmp2+=1
        else :
            if tmp2 > 0 :
                break
            st2 = cnt     
    
    # 흡연정보
    st3 = 0
    tmp3=0
    for cnt, i in enumerate(df_smoke.iloc[:,0]) :
        if i == j :
            if tmp3 == 0:
                st3 = cnt
            tmp3+=1
        else :
            if tmp3 > 0 :
                break
            st3 = cnt     
    
    # 투약정보
    st4 = 0
    tmp4=0
    for cnt, i in enumerate(df_drug.iloc[:,0]) :
        if i == j :
            if tmp4 == 0:
                st4 = cnt
            tmp4+=1
        else :
            if tmp4 > 0 :
                break
            st4 = cnt
    
    # EGC - 한줄정보
    st5 = 0
    tmp5=0
    for cnt, i in enumerate(df_egc.iloc[1:,5]) :
        if i == j :
            st5 = cnt
            break
    
    # 데이터 슬라이싱
    b=df_c_egc.iloc[st : st+tmp]
    c=df_hw.iloc[st2 : st2+tmp2, 1:]
    d=df_smoke.iloc[st3 : st3+tmp3, 1:]
    e=df_drug.iloc[st4 : st4+tmp4, 1:]
    f=df_egc.iloc[st5+1 : st5+2]
    
    # 채혈,채뇨검사 정보보다 다른 정보가 많을 경우 -> 채혈,채뇨검사 정보에 빈 행들 추가
    if len(b) < max(len(b),len(c),len(d),len(e),len(f)) :
            lgth = max(len(b),len(c),len(d),len(e),len(f)) - len(b)
            for j in range(1,lgth+1) :
                b=b.append(pd.Series(name=st+tmp+j))
    
    ## 데이터 프레임 합치기
    if j==9070599 :  # 맨 처음 데이터 일 때(첫 번째 환자 등록번호)
        a=pd.concat([b,c.set_index([b.index[:len(c)]])], axis=1)            
        a=pd.concat([a,d.set_index([a.index[:len(d)]])], axis=1)
        a=pd.concat([a,e.set_index([a.index[:len(e)]])], axis=1)        
        a=pd.concat([a,f.set_index([a.index[:len(f)]])], axis=1)
    else :
        b=pd.concat([b,c.set_index([b.index[:len(c)]])], axis=1)            
        b=pd.concat([b,d.set_index([b.index[:len(d)]])], axis=1)
        b=pd.concat([b,e.set_index([b.index[:len(e)]])], axis=1)        
        b=pd.concat([b,f.set_index([b.index[:len(f)]])], axis=1)
        a=pd.concat([a,b], axis=0) 
        
a.to_excel('전처리데이터_1차.xlsx', encoding='utf-8-sig', index=False)