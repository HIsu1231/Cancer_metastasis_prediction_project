import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

## 전처리된 데이터 가져오기
path_file_c_egc = './전처리된 데이터/CEL1.xlsx' #Clinical_EGC_sheet합침
path_file_egc = './전처리된 데이터/EGC_main.xlsx'

df_c_egc = pd.read_excel(path_file_c_egc)
df_egc = pd.read_excel(path_file_egc)

### 전처리 4차 - 채혈/채뇨일자(오름차순) / 검사명 (검사명1-번호, 검사명2-번호) 형태로 세로로 concat

## 환자명 제거
df_egc.drop('이름',axis=1, inplace=True)

## 중복되는 컬럼명 수정
df_c_egc.rename(columns={'처방코드':'C_EGC_처방코드'}, inplace=True)

## padding - 결측값 : -1, 빈 값 : 0 , 두 번째 행에 N값 추가
ddel1 = df_c_egc[df_c_egc['이름'].str.contains('한상준')].index
df_4 = df_c_egc.drop(ddel1, inplace=False)
ddel2 = df_egc[df_egc['이름'].str.contains('한상준')].index
df_egc_2 = df_egc.drop(ddel2, inplace=False)

for i in range(len(df_4)) :
    df_4.iloc[i,13] = df_4.iloc[i,13][2:10]
    
## 채혈일시에서 '-' 제거 : 일시에 숫자 6개만 남기기
df_4.iloc[:,13].replace(to_replace='[-]',value='',regex=True, inplace=True) # 정규식 표현
df_4.rename(columns={'채혈일시':'date'}, inplace=True)

## Monocytes, Eosinophils 추출
df_ins1=df_4[df_4['검사명'].str.contains('Monocytes', na=False, regex=False)]
df_ins2=df_4[df_4['검사명'].str.contains('Eosinophils', na=False, regex=False)]

## 날짜 오름차순 정렬
df_ins1 = df_ins1.sort_values('date')
df_ins2 = df_ins2.sort_values('date')

## 데이터 삽입
for i in df_egc_2.iloc[:,6] : # i = 등록번호
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

    # 일시 중복제거 
    dtlst1 = df_ins1[df_ins1['등록번호']==i]['date']
    dtlst2 = df_ins2[df_ins2['등록번호']==i]['date']
    dtlst1 = pd.concat([dtlst1,dtlst2], axis=0)
    dtlst1 = dtlst1.sort_values().dropna() # sort_values()
    dtlst1 = dtlst1.unique()
    
    # 컬럼 만들기
    name_ins1 = str(int(i)) + '_Monocytes'
    name_ins2 = str(int(i)) + '_Eosinophils'
    
    # 한 사람당 날짜별 데이터 만들기
    for x, dt in enumerate(dtlst1) : 
        name_dt = pd.DataFrame({'date':[dt]})
        if (df_ins1_1.iloc[:,13]==dt).any() :
            tmp_ins1 = pd.DataFrame({name_ins1:[df_ins1_1[df_ins1_1['date']==dt].iat[0,11]]})
        elif not (df_ins1_1.iloc[:,13]==dt).any() :
            tmp_ins1 = pd.DataFrame({name_ins1:[-1]})
        
        if (df_ins2_1.iloc[:,13] == dt).any() :
            tmp_ins2 = pd.DataFrame({name_ins2:[df_ins2_1[df_ins2_1['date']==dt].iat[0,11]]})
        elif not (df_ins2_1.iloc[:,13] == dt).any() :
            tmp_ins2 = pd.DataFrame({name_ins2:[-1]})
        tmpc = pd.concat([name_dt, tmp_ins1], axis=1)
        tmpc = pd.concat([tmpc, tmp_ins2], axis=1)
        
        if x == 0:
            tempc = tmpc
        else :  
            tempc = pd.concat([tempc, tmpc], axis=0)
        
    tempc = tempc.reset_index(drop=True)
    
    ## 데이터 프레임 합치기
    if i == 9070599 : # 맨 처음 데이터 일 때(첫 번째 환자 등록번호)
        a=tempc
    else :
        a=pd.concat([a,tempc], axis=1)
        
a.fillna(0)
a.to_excel('전처리데이터_4차_test.xlsx', encoding='utf-8-sig', index=False)

## N 임베딩 시키기
df_n = df_egc.loc[:,['등록번호','N.1']]

for i in range(len(df_n)) :
    n_name = 'n_' + str(i)
    n = pd.DataFrame({n_name : [df_n.iloc[i,1]]})
    if i == 0 :
        tmpn = pd.concat([n,n], axis=1)
        tmpn = pd.concat([tmpn,n], axis=1)
    else :
        tmpn = pd.concat([tmpn,n],axis=1)
        tmpn = pd.concat([tmpn,n], axis=1)
        tmpn = pd.concat([tmpn,n], axis=1)

tmpn.to_excel('N데이터.xlsx',encoding='utf-8-sig', index=False)
