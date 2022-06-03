import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

## 전처리된 데이터 가져오기
path_file_c_egc = './전처리된 데이터/CEL1.xlsx' #Clinical_EGC_sheet합침
path_file_egc = './전처리된 데이터/EGC_main.xlsx'

df_c_egc = pd.read_excel(path_file_c_egc)
df_egc = pd.read_excel(path_file_egc)

### 전처리 3차 - 등록번호 별 tumor maker (tumormaker1-번호, tumormaker2-번호) 형태로 세로로 concat

## 환자명 제거
df_egc.drop('이름',axis=1, inplace=True)

## 중복되는 컬럼명 수정
df_c_egc.rename(columns={'처방코드':'C_EGC_처방코드'}, inplace=True)

## 데이터 없는 사람 제거
ddel1 = df_c_egc[df_c_egc['이름'].str.contains('한상준')].index
df_4 = df_c_egc.drop(ddel1, inplace=False)
ddel2 = df_egc[df_egc['이름'].str.contains('한상준')].index
df_egc_2 = df_egc.drop(ddel2, inplace=False)

## tumor maker 추출
# df_ins - 등록번호별로 검사명과 검사결과 갖고오기
df_ins1=df_4[df_4['검사명'].str.contains('CEA(S)', na=False, regex=False)] 
df_ins2=df_4[df_4['검사명'].str.contains('CA19-9(RIA)', na=False, regex=False)]

## tumor maker concat
for i in df_egc_2.iloc[:,6] :
    st = 0
    for cnt, j in enumerate(df_egc_2.iloc[:,6]) : # cnt는 0부터 시작
        if j == i :
            st=cnt
            break
    
    # 등록번호에 맞춰 CEA(S), CA19-9(RIA) 가져오기
    df_ins1_1 = df_ins1[df_ins1['등록번호']==i]
    df_ins2_1 = df_ins2[df_ins2['등록번호']==i] 
    
    
    # CEA(S), CA19-9(RIA) 중 더 긴 데이터에 맞춰 널값 생성
    len_ins1 = len(df_ins1_1)
    len_ins2 = len(df_ins2_1)
    mxlen = max(len_ins1, len_ins2)
    
    for t in range(len_ins1, mxlen) :
        df_ins1_1 = df_ins1_1.append(pd.Series(name=t))
    for t in range(len_ins2, mxlen) :
        df_ins2_1 = df_ins2_1.append(pd.Series(name=t))

    # 컬럼 만들기
    name_ins1 = str(int(i)) + '_CEA(S)'
    name_ins2 = str(int(i)) + '_CA19-9(RIA)'
    
    # 한 사람당 데이터 만들기 -> tempc
    for k in range(mxlen) :
        tmp_ins1 = pd.DataFrame({name_ins1:[df_ins1_1.iloc[k,11]]})
        tmp_ins2 = pd.DataFrame({name_ins2:[df_ins2_1.iloc[k,11]]})
        tmpc = pd.concat([tmp_ins1, tmp_ins2], axis=1)
        if k == 0 :
            tempc = tmpc
        else :
            tempc = pd.concat([tempc, tmpc], axis=0)
        
    tempc = tempc.reset_index(drop=True)

    if i == 9070599 :
        a=tempc
    else :
        a=pd.concat([a,tempc], axis=1)

a.to_excel('전처리데이터_3차.xlsx', encoding='utf-8-sig', index=False)