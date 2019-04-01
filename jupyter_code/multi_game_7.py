#!/usr/bin/env python
# coding: utf-8

# In[3]:


# 数据读取
import pandas as pd
df = pd.read_csv('../data/multi_game_7.csv')

# 选取流失天数低于14天[0,14]
loss_data = df[(df['lostdays']<=14)]

loss_data.head(20)


# In[65]:


loss_data[['gname_1','gname_2','gname_3','gname_4','gname_5','gname_6','gname_7']][0:1]


# In[5]:


# t统计流失用户分布
loss_data['lostdays'].value_counts().sort_index().plot()


# In[6]:


# 获取所有用户的游戏局数分布,去掉非0比例数据
game_rate = loss_data[['game1_rate','game2_rate','game3_rate','game4_rate','game5_rate','game6_rate','game7_rate']]

game_rate_data = game_rate.loc[(game_rate['game1_rate']>0.0) 
                             | (game_rate['game2_rate']>0.0) 
                             | (game_rate['game3_rate']>0.0)
                             | (game_rate['game4_rate']>0.0)
                             | (game_rate['game5_rate']>0.0)
                             | (game_rate['game6_rate']>0.0)
                             | (game_rate['game7_rate']>0.0)]


# In[15]:


# 处理数据
# 1. 向量化
X = game_rate_data.values
X


# In[16]:


# 引入包
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt


# In[17]:


# 迭代Kmeans
def k_means_iter(n_cluster,init_cluster=3):
    '''
    init : 默认初始3类,n_cluster: 最大分类数
    '''
    
    # 构建空列表用于存储总的簇内离差平方和
    TSSE=[]
    # 迭代分类数
    K = range(init_cluster,n_cluster+1,1)
    for k in K:
        # 用于存储各个簇内离差平方和
        SSE=[]
        # KMeans模型的构建和训练
        kmeans=KMeans(n_clusters=k).fit(X)
        # 返回簇标签
        labels=kmeans.labels_
        # 返回簇中心
        centers=kmeans.cluster_centers_
        
        #print ('Cluster: '+ str(k) +' \t Center: '+ str(centers))
        # 计算各簇样本的离差平方和
        for label in set(labels):
            SSE.append(np.sum((game_rate_data.loc[labels==label]-centers[label])**2))
        # 计算总的簇内离差平方和
        TSSE.append(np.sum(SSE))
     
    fig = plt.gcf()
    fig.set_size_inches(16, 10)
    
    # 设置绘图风格
    plt.style.use('ggplot')
    # 绘制K的个数与TSSE的关系
    plt.plot(K,TSSE,'b*-')
    plt.xlabel('n_cluster',fontsize=20)
    plt.ylabel('SSE',fontsize=20)
    plt.tight_layout()


# In[19]:


k_means_iter(10,init_cluster=1)


# In[11]:


# 分6类
kmeans_cluster = KMeans(n_clusters=6).fit(X)


# In[12]:


# 中心点
centers = kmeans_cluster.cluster_centers_
centers


# In[13]:


# 点的标签
game_rate_data['cluster'] = kmeans_cluster.labels_
game_rate_data.head(20)


# In[56]:


lr_game_rate = loss_data[['lostdays','game1_rate','game2_rate','game3_rate','game4_rate','game5_rate','game6_rate','game7_rate']]

lr_game_rate_data = lr_game_rate.loc[(lr_game_rate['game1_rate']>0.0) 
                             | (lr_game_rate['game2_rate']>0.0) 
                             | (lr_game_rate['game3_rate']>0.0)
                             | (lr_game_rate['game4_rate']>0.0)
                             | (lr_game_rate['game5_rate']>0.0)
                             | (lr_game_rate['game6_rate']>0.0)
                             | (lr_game_rate['game7_rate']>0.0)]


# In[57]:


lr_X = lr_game_rate_data[['game1_rate','game2_rate','game3_rate','game4_rate','game5_rate','game6_rate','game7_rate']]

lr_X.head(5)


# In[58]:


# tmp_Y = pd.DataFrame(15 - lr_game_rate_data['lostdays']).T
lr_game_rate_data.loc[(lr_game_rate_data['lostdays']<=7)] = 0
lr_game_rate_data.loc[(lr_game_rate_data['lostdays']>7)] = 1
tmp_Y = pd.DataFrame(lr_game_rate_data['lostdays']).T
tmp_Y


# In[59]:


from sklearn import utils
from sklearn import preprocessing

l_Y = preprocessing.normalize(tmp_Y,norm='l2')[0][0:]
# 格式化数据类型
lab_enc = preprocessing.LabelEncoder()
lr_Y = lab_enc.fit_transform(l_Y)

utils.multiclass.type_of_target(lr_Y)

lr_Y[0:100]


# In[60]:


from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(solver='liblinear',penalty='l2',multi_class='ovr')
lr.fit(lr_X,lr_Y)


# In[61]:


lr.coef_ 


# In[62]:


lr.classes_ 


# In[64]:


lr.intercept_


# In[ ]:




