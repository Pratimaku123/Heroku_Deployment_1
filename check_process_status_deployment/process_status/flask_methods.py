from flask import Flask, jsonify, request,render_template,url_for,flash
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

app = Flask(__name__)

def get_server_list():
    os.system('sshpass -p "Algo_2021" ssh pratima@ninja100.ndc.aptportfolio.com "./list_of_servers.py" > /home/pkumari/Desktop/DeepLearning/Revision_DS/DataVis_Seaborn/server_list.csv')
    server_df=pd.read_csv('/home/pkumari/Desktop/DeepLearning/Revision_DS/DataVis_Seaborn/server_list.csv',header=None)
    cols=server_df.columns.to_list()
    server_name=[]
    for col in cols:
        server_name.append(server_df[col][0].strip('[]').strip(" '"))
    
    remove_server=['nemo45','nemo27','nemo73','nemo105','nemo69']
    for srv in remove_server:
        server_name.remove(srv)

    l=[int(x.split("o")[-1]) for x in server_name]
    l1=sorted(l)
    server_list=["nemo"+str(x) for x in l1]

    return server_list

def server_status():
    path=os.getcwd()
    images=os.listdir('static')
    for img in images:
        os.remove(path+'/static/'+img)

    server_name=get_server_list()
    # server_list=['nemo81', 'nemo85', 'nemo87', 'nemo25', 'nemo13', 'nemo10', 'nemo11', 'nemo35', 'nemo30', 'nemo79', 'nemo209', 'nemo53', 'nemo77', 'nemo98', 'nemo93', 'nemo97', 'nemo95', 'nemo57', 'nemo67', 'nemo49', 'nemo47', 'nemo51']
    for server in server_name:
        hostname="pratima@"+server+".nse.aptportfolio.com"

        os.system('sshpass -p "Algo_2021" ssh {} "check_trade_process" > /home/pkumari/Desktop/DeepLearning/Revision_DS/DataVis_Seaborn/process_status.csv'.format(hostname))

        df=pd.read_csv('/home/pkumari/Desktop/DeepLearning/Revision_DS/DataVis_Seaborn/process_status.csv',header=None)

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
        df1=df.copy()
        df1['process']=df1['process']+'_'+df1['user']

        fig=plt.figure(figsize=(8,7))
        sns.heatmap(pd.pivot_table(data=df1,index='process',values='status',fill_value=0),annot=True,cmap="RdYlGn",vmin=0,vmax=1)
        plt.title(server,fontdict={'color':'Blue','fontweight':25,'fontsize':20})
        fig.savefig('static/'+server+'.png',dpi=300,bbox_inches='tight')

    images=os.listdir('static')
    return images

# @app.route('/')
# def index():
#     return render_template('index.html', servers = server_name)

@app.route('/')
def index():
    servers=get_server_list()
    return render_template('index.html', servers = servers)

@app.route('/status')   
def home():
    hists = server_status()
    return render_template('home.html', hists = hists)



if __name__ == "__main__":
    app.run(debug=True)
