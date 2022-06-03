import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

## 전처리된 데이터 가져오기
path_file_c_egc = './전처리된 데이터/CEL1.xlsx' #Clinical_EGC_sheet합침
path_file_smoke = './전처리된 데이터/흡연정보2.xlsx' 
path_file_egc = './전처리된 데이터/EGC_main.xlsx'

df_c_egc = pd.read_excel(path_file_c_egc)
df_smoke = pd.read_excel(path_file_smoke)
df_egc = pd.read_excel(path_file_egc)

### 전처리 2차 - 등록번호, 나이, 성별, 흡연정보(라벨링), 기록일시, tumor maker(n개) 한 행에 저장 후 세로로 concat

## 환자명 제거
df_smoke.drop('환자명',axis=1, inplace=True)

## 중복되는 컬럼명 수정
df_smoke.rename(columns={'기록일시':'흡연_기록일시'}, inplace=True)

## 데이터 없는 사람 제거
ddel1 = df_c_egc[df_c_egc['이름'].str.contains('한상준')].index
df_2 = df_c_egc.drop(ddel1, inplace=False)
ddel2 = df_egc[df_egc['이름'].str.contains('한상준')].index
df_egc_2 = df_egc.drop(ddel2, inplace=False)

## 흡연정보 라벨링 -> 0(과거흡연), 1(비흡연), 2(현재흡연), 3(확인불능)
mapping={'과거흡연':0, '비흡연':1, '현재흡연':2, '확인불능':3}
mp = df_smoke['흡연정보'].map(mapping)
df_smoke_mp = df_smoke.drop('흡연정보', axis=1)
df_smoke_mp.insert(2,'흡연정보',mp)

## df_info - 등록번호, 나이, 성별, N_target DF 저장
df_sinfo = df_egc_2.loc[:,['등록번호','나이','성별','N.1']] # 이 뒤에 흡연정보, 피검사 기록 concat

## tumor maker 추출
df_ins1=df_2[df_2['검사명'].str.contains('CEA(S)', na=False, regex=False)]
df_ins2=df_2[df_2['검사명'].str.contains('CA19-9(RIA)', na=False, regex=False)]

##  concat
# df_ins - 등록번호별로 검사명과 검사결과 갖고오기
# 제일 긴 검사 수 세서 세로로 NaN값 넣기
mx = 0
for i in df_egc_2.iloc[:, 6] :
    tmp1 = 0
    tmp2 = 0
    for j in df_ins1.iloc[:,2] :
        if j == i :
            tmp1 += 1
    for k in df_ins2.iloc[:,2] :
        if k == i :
            tmp2 += 1
    if tmp1 > mx :
        mx = tmp1
    if tmp2 > mx : 
        mx = tmp2

for i in df_egc_2.iloc[:, 6]  :
    # 한 줄 데이터 EGC
    st = 0
    for cnt, k in enumerate(df_egc_2.iloc[:,6]) : # cnt는 0부터 시작
        if k == i :
            st=cnt
            break  

    # 흡연기록
    st2 = 0
    tmp2 = 0
    for cnt, k in enumerate(df_smoke_mp.iloc[:,0]) :
        if k == i :
            if tmp2 == 0 :
                st2 = cnt
            tmp2+=1
        else :
            if tmp2 > 0 :
                break
            st2 = cnt     
    
    b=df_sinfo.iloc[st:st+1] # 한 줄 데이터
    c=df_smoke_mp.iloc[st2 : st2+tmp2, 1:]    
    
    if len(b) < len(c) :
        lgth = len(c) - len(b)
        for j in range(1,lgth+1) :
            b=b.append(pd.Series(name=st+j))   
    
    df_ins1_1 = df_ins1[df_ins1['등록번호']==i]
    df_ins2_1 = df_ins2[df_ins2['등록번호']==i] 

    ## CEA(S), CA19-9(RIA) 개수가 다를 경우 부족한 공간에 NaN
    len_ins1 = len(df_ins1_1)
    len_ins2 = len(df_ins2_1)
    mxlen = max(len_ins1, len_ins2)

    for t in range(len_ins1, mx) :
        df_ins1_1 = df_ins1_1.append(pd.Series(name=t))

    for t in range(len_ins2, mx) :
        df_ins2_1 = df_ins2_1.append(pd.Series(name=t))

    # 컬럼 만들기
    name_ins1 = 'CEA(S)'
    name_ins2 = 'CA19-9(RIA)'

    ## CEA, CA 데이터 합치는 코드
    for j in range(mx) :
        tmp_ins1 = pd.DataFrame({name_ins1:[df_ins1_1.iloc[j,11]]})
        tmp_ins2 = pd.DataFrame({name_ins2:[df_ins2_1.iloc[j,11]]})
        if j == 0 :
            tmpc = pd.concat([tmp_ins1, tmp_ins2], axis=1)
        else :
            tmpc = pd.concat([tmpc,tmp_ins1], axis=1)
            tmpc = pd.concat([tmpc,tmp_ins2], axis=1)

            
    #tmpc = tmpc.reset_index(drop=True)
     
    
    ## 데이터 프레임 합치기
    if i==9070599 : # 맨 처음 데이터 일 때(첫 번째 환자 등록번호)
        a=pd.concat([b,c.set_index([b.index[:len(c)]])], axis=1)
        a=pd.concat([a,tmpc.set_index([a.index[:len(tmpc)]])], axis=1)
    else :
        b=pd.concat([b,c.set_index([b.index[:len(c)]])], axis=1)
        b=pd.concat([b,tmpc.set_index([b.index[:len(tmpc)]])], axis=1)
        a=pd.concat([a,b], axis=0)
        
a.to_excel('전처리데이터_2차.xlsx', encoding='utf-8-sig', index=False)