import pandas as pd

## 원본 데이터 가져오기
path_file_drug = './의정부성모데이터_최종/투약기록_20220426.xlsx'
path_file_c_egc = './의정부성모데이터_최종/Clinical_EGC_labdata.xlsx' ## sheet 여러개
path_file_hw = './의정부성모데이터_최종/키_몸무게_20220426.xlsx'
path_file_smoke = './의정부성모데이터_최종/흡연정보.xlsx'
path_file_egc = './의정부성모데이터_최종/EGC_20220509.xlsx' ## sheet 여러개

df_drug = pd.read_excel(path_file_drug)
df_c_egc = pd.read_excel(path_file_c_egc,sheet_name=None) # sheet_name=None : 전체 시트 가져오기
df_hw = pd.read_excel(path_file_hw)
df_smoke = pd.read_excel(path_file_smoke)
df_egc = pd.read_excel(path_file_egc, sheet_name='Main')

### 전처리에 들어가면 안 되는 데이터 제거
## 투약기록 - 2군 삭제
drug_del = df_drug[df_drug['처방명'].str.contains('2군')].index
df_drug.drop(drug_del, inplace=True)

df_drug.to_excel("투약기록_2군제거.xlsx", encoding='utf-8-sig', index=False)

## Clinical_EGC_labdata 한 시트에 합치기
for j in range(1,len(df_c_egc.keys())) :
    idx='Data_'
    idx+=str(j)
    if j == 1 :
        tmp = pd.concat([df_c_egc['Data'], df_c_egc[idx]])
    else :
        tmp = pd.concat([tmp, df_c_egc[idx]])
df_c_egc = tmp

df_c_egc.to_excel("Clinilcal_EGC_labdata_prepro.xlsx", encoding='utf-8-sig', index=False)