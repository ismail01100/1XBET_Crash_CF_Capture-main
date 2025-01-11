import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import lightgbm as lgb
import catboost as cb

df=pd.read_csv('data.csv',header=None)
df.columns=['Round', 'Time', 'Numberofplayers', 'totalbet', 'totalwinning', 'onCash']
df['Round']=df['Round'].map(lambda x: x[-1])
df['Time']=df['Time'].map(lambda x: x[len('time: '):])
df['Numberofplayers']=df['Numberofplayers'].map(lambda x: x[len('Numberofplayers: '):])
df['totalbet']=df['totalbet'].map(lambda x: x[len('totalbet: '):])
df['totalwinning']=df['totalwinning'].map(lambda x: x[len('totalwinning: '):])
df['onCash']=df['onCash'].map(lambda x: x[len('onCash: '):])

for i in df.columns:
    if i=='Time':
        continue
    df[i]=df[i].astype(np.float32)


for i in df.where(df['Time']=='0').dropna().index:
    df.drop(i,inplace=True)


for i in df.where(df['Numberofplayers']=='0').dropna().index:
    df.drop(i,inplace=True)


df['hour']=df['Time'].map(lambda x: x.split(':')[0])
df['minutes']=df['Time'].map(lambda x: x.split(':')[1])
df['seconds']=df['Time'].map(lambda x: x.split(':')[2])


df.drop(['Time'],axis=1,inplace=True)


for i in df.columns:
    df[i]=df[i].astype(np.float32)


def resultat_nonverbose(input):
    model_xgboost = XGBRegressor()
    model_xgboost.load_model('xgboost_regression_model.json')


    preds1 = model_xgboost.predict(input)
    bst = lgb.Booster(model_file='lightgbm_regression_model.txt')
    

    preds2 = bst.predict(input)

    

    model = cb.CatBoostRegressor()
    model.load_model('catboost_regression_model.cbm')



    # Make predictions
    preds3 = model.predict(input)

    

    avg_xgboost_lgboost= (preds1.item()+preds2.item())/2

   


    avg_lgboost_catboost= (preds2.item()+preds3.item())/2

    

    return (round(avg_xgboost_lgboost,2)+round(avg_lgboost_catboost,2))/2




df_test=df.drop(['onCash'],axis=1)

print(df.iloc[-1]['onCash'])
print(resultat_nonverbose([df_test.iloc[-1]]))