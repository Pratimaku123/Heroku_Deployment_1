from flask import Flask, jsonify, request,render_template,url_for,flash ,redirect
import os
import getpass,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from multiprocessing import Pool
#import Tkinter

user=getpass.getuser()
print(user)
home_path='/home/'+user+'/'
app = Flask(__name__)

def get_server_list(server):
    print('we are inside get_server_list function for server name {}'.format(server))
    
#    for server in server_name:
    try:
        hostname=user+"@"+server+".nse.aptportfolio.com"

        os.system('ssh {} "check_trade_process" > {}check_process_status_deployment/process_status/process_status_{}.csv'.format(hostname,home_path,server))
        df=pd.read_csv('{}check_process_status_deployment/process_status/process_status_{}.csv'.format(home_path,server),header=None)

        if ((df.loc[0][0].startswith('CRITICAL: Config not found for')) or(df.loc[0][0].endswith('command not found'))):
            return
        else:
            return server
    except Exception as e:
        print('excpetion occur while reading file:{} {}'.format(server,str(e)))
        os.system('cat {}check_process_status_deployment/process_status/process_status_{}.csv'.format(home_path,server))
         
   # print(actual_server)

   # l=[int(x.split("o")[-1]) for x in actual_server]
   # l1=sorted(l)
   # server_list=["nemo"+str(x) for x in l1]
   # with open('{}check_process_status_deployment/process_status/server_list.csv'.format(home_path),'w') as f:
   #     l1=map(lambda x:x+',', server_list)
   #     f.writelines(l1)
   # f.close()

   # return server_list

def get_all_server_list():
    server_df=pd.read_csv('{}check_process_status_deployment/process_status/server_list.csv'.format(home_path),header=None)
    cols=server_df.columns.to_list()
    server_name=[str(server_df[col][0]) for col in cols]
    server_name.pop()

    return server_name


def server_status(server):
    images=os.listdir('{}check_process_status_deployment/process_status/static'.format(home_path))
    for img in images:
        os.remove('{}check_process_status_deployment/process_status/static/'.format(home_path)+img)

    print('getting server status for {}'.format(server))
    hostname=user+"@"+server+".nse.aptportfolio.com"

    os.system('ssh {} "check_trade_process" > {}check_process_status_deployment/process_status/process_status_{}.csv'.format(hostname,home_path,server))

    df=pd.read_csv('{}check_process_status_deployment/process_status/process_status_{}.csv'.format(home_path,server),header=None)

    df.columns=['des']
    df['process']=df["des"].apply(lambda x:x.split("running as")[0].split(":")[1].split(" ")[1].split("./")[1] if x.split("running as")[0].split(":")[1].split(" ")[1][:2]=="./"
                        else x.split("running as")[0].split(":")[1].split(" ")[1])
    df['user']=df['des'].apply(lambda x:x.split("running as")[1].split(" ")[1])
    df['expected']=df['des'].apply(lambda x:x.split("(")[1].split(")")[0].split(" ")[0].split(":")[1])
    df['actual']=df['des'].apply(lambda x:x.split("(")[1].split(")")[0].split(" ")[1].split(":")[1])
    df['status']=df['des'].apply(lambda x:x.split(":")[0])
    df.drop("des",axis=1,inplace=True)
    df['actual']=df['actual'].astype("int")
    df['expected']=df['expected'].astype("int")
    df['status']=df['status'].apply(lambda x:1 if x=="OK" else 0)
    print(df)
    df1=df.copy()
    df1['process']=df1['process']+'_'+df1['user']

    fig=plt.figure(figsize=(8,7))
    sns.heatmap(pd.pivot_table(data=df1,index='process',values='status',fill_value=0),annot=True,cmap="RdYlGn",vmin=0,vmax=1)
    plt.title(server,fontdict={'color':'Blue','fontweight':25,'fontsize':20})
    fig.savefig('{}check_process_status_deployment/process_status/static/'.format(home_path)+server+'.png',dpi=300,bbox_inches='tight')
    print('fig save for {}'.format(server)
    images=os.listdir('{}check_process_status_deployment/process_status/static'.format(home_path))
    for img in images:
        print('image present in imaglist {}'.format(img))
        return img



@app.route('/')
def index():

    os.system('ssh {}@ninja100.ndc.aptportfolio.com "python {}check_process_status_deployment/process_status/list_of_servers.py" > {}check_process_status_deployment/process_status/server_list.csv'.format(user,home_path,home_path))
    server_df=pd.read_csv('{}check_process_status_deployment/process_status/server_list.csv'.format(home_path),header=None)
    cols=server_df.columns.to_list()
    server_name=[server_df[col][0].strip('[]').strip(" '") for col in cols]

    p=Pool(5)
    servers=p.map(get_server_list,server_name)
    for s in servers:
        if s==None:
            servers.remove(s)
        else:
            pass

    l=[int(x.split("o")[-1]) for x in servers]
    l1=sorted(l)
    server_list=["nemo"+str(x) for x in l1]
    print(server_list)

    with open('{}check_process_status_deployment/process_status/server_list.csv'.format(home_path),'w') as f:
        l1=map(lambda x:x+',', server_list)
        f.writelines(l1)
    f.close()

    return render_template('index_1.html', servers = server_list)

@app.route('/status',methods=['POST','GET']) 
def home():
    if request.method == 'POST':
        srvs_request= request.form.getlist('checkbox_done')
        
        print(srvs_request)
        images=os.listdir('{}check_process_status_deployment/process_status/static'.format(home_path))
        for img in images:
            os.remove('{}check_process_status_deployment/process_status/static/'.format(home_path)+img)


        if ('ALL' not in srvs_request ):
            p=Pool(10)
            hists = p.map(server_status,srvs_request)
            print(hists)
            return render_template('home.html',hists=hists)
        elif(('ALL' in srvs_request) and (len(srvs_request)==1)):
            p=Pool(10)
            servers =get_all_server_list()
            hists = p.map(server_status,servers)
            return render_template('home.html',hists=hists)
        elif len(srvs_request==0):
            return 'nothing has been passed {}'.format(srvs_request)




if __name__ == "__main__":
    app.run(debug=True)
