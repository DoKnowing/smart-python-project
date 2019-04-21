#!/usr/bin/env python
# coding: utf-8

# In[22]:


import pandas as pd

df = pd.read_csv('../data/vn_month_user.csv')

df.head(20)


# In[2]:


lr_X = df[['login_days','max_series_days','loss_days','is_new_user']]
lr_X.head(5)


# In[3]:


lr_Y = df[['is_loss']]


# In[37]:


from sklearn.feature_selection import SelectKBest, chi2,f_classif,mutual_info_classif
# f_classif,chi2,mutual_info_classif
skb = SelectKBest(mutual_info_classif, k=2)


# In[42]:


X_new = skb.fit_transform(lr_X, lr_Y)


# In[43]:


skb.get_params()


# In[44]:


skb.scores_ 


# In[45]:


X_new


# In[47]:


tmp = df[['login_days','max_series_days','loss_days','is_new_user','is_loss']]
tmp.head(20)


# In[86]:


import math
math.log(8)


# In[32]:


import math
# 计算H(D) 信息增益
def gain_d(data):
    pi = data.value_counts() / data.shape[0]
    hx = 0.0
    for p in pi:
        hx += -1.0 * p * math.log(p,2)
    return hx

# 计算特征字段 信息增益
def gain(data,columns=[]):
    if len(columns)==0:
        columns = data.columns
    # 计算Di
    di = data[columns[0]].value_counts() / data.shape[0]
    # 计算H(D)
    hd = gain_d(data[columns[1]])
    hda = 0.0
    for key in di.keys():
        # 计算 H(Di)
        hda += gain_d(data[(data[columns[0]] == key)][columns[1]]) * di[key]
    return hd-hda


# In[31]:


tmp = df[['login_days','max_series_days','loss_days','is_new_user','reg_days','is_loss']]
columns = tmp.columns
for c in columns[0:-1]:
    cs = []
    cs.append(c)
    cs.append(columns[-1])
    print (c+" : " + str(gain(tmp[cs])))


# In[33]:


gain(df[['reg_days','is_loss']])


# In[35]:


import pandas as pd

test = pd.read_csv('../data/test_5-1.csv')

test


# In[124]:


# 计算 gini 系数. 
def gini_d(data):
    return 1.0-sum(pow(data.value_counts() / data.shape[0],2))

# 计算特征字段 gini 系数. 
def gini(data,columns=[]):
    if len(columns)==0:
        columns = data.columns
    # 计算 Ck
    ck = data[columns[0]].value_counts() / data.shape[0]
    min_gina_da = 1.0
    for key in ck.keys():
        gina_da = gini_d(data[(data[columns[0]] == key)][columns[1]]) * ck[key]             + gini_d(data[(data[columns[0]] != key)][columns[1]]) * (1.0-ck[key])
        if gina_da<=min_gina_da:
            min_gina_da = gina_da
    return min_gina_da


# In[125]:


gini(test[['age','is_good']])


# In[118]:


tmp = test[['age','has_job','has_house','credit','is_good']]
columns = tmp.columns
for c in columns[0:-1]:
    cs = []
    cs.append(c)
    cs.append(columns[-1])
    print (c+" : " + str(gini(tmp[cs])))


# In[120]:


tmp = test[['age','has_job','has_house','credit','is_good']]
columns = tmp.columns
for c in columns[0:-1]:
    cs = []
    cs.append(c)
    cs.append(columns[-1])
    print (c+" : " + str(gini(tmp[cs])))


# In[41]:


lr_X_2 = test[['age','has_job','has_house','credit']]
lr_Y_2 = test['is_good']


# In[60]:


# 决策树
from sklearn.tree import DecisionTreeClassifier,ExtraTreeClassifier

clf = ExtraTreeClassifier(criterion='gini',splitter='best')
clf.fit(lr_X_2,lr_Y_2)

from sklearn.tree import export_graphviz
from  sklearn import tree
# import pydotplus

#画图方法1-生成dot文件

tree.export_graphviz(clf, out_file='./treeone_test.dot',proportion=True,rotate=True,feature_names=['age','has_job','has_house','credit'])
# tree.export_graphviz(clf, out_file='./treeone_test.dot',proportion=True,rotate=True)


# In[90]:


gini_d(test['is_good'])


# In[92]:


gini_d(test[test['has_house']==0]['is_good'])


# In[100]:


gini_d(test[(test['has_house']==0) & (test['credit']!=0)]['is_good'])


# In[79]:


test[(test['is_good']==0) & (test['credit']!=1)]


# In[102]:


test[(test['has_house']==0) & (test['credit']!=0)].shape[0] * 1.0 / test.shape[0]


# In[103]:


test[(test['has_house']==0) & (test['credit']>0.5) & (test['has_job']<=0.5)].shape[0] * 1.0 / test.shape[0]


# In[ ]:




